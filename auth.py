import os
import json
import requests
from jose import jwt
from jose.utils import base64url_decode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import boto3
from botocore.exceptions import ClientError

# Configurar logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Obter configurações do Cognito
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")
COGNITO_SECRET_NAME = os.environ.get("COGNITO_SECRET_NAME", "projeto-vida/cognito")

# URL para obter as chaves públicas
keys_url = f"https://cognito-idp.{REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

oauth2_scheme = HTTPBearer(auto_error=False)

def get_cognito_config():
    """Recupera configurações do Cognito do Secrets Manager ou variáveis de ambiente"""
    try:
        # Tentar obter do Secrets Manager
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # Estamos no Lambda?
            secretsmanager_client = boto3.client('secretsmanager')
            try:
                response = secretsmanager_client.get_secret_value(SecretId=COGNITO_SECRET_NAME)
                secret = json.loads(response['SecretString'])
                return {
                    'region': secret.get('region', REGION),
                    'user_pool_id': secret.get('user_pool_id', COGNITO_USER_POOL_ID),
                    'app_client_id': secret.get('app_client_id', COGNITO_APP_CLIENT_ID)
                }
            except ClientError as e:
                logger.warning(f"Erro ao recuperar segredo do Cognito: {str(e)}")
                # Continuar com variáveis de ambiente
    except Exception as e:
        logger.warning(f"Erro geral ao obter configuração do Cognito: {str(e)}")
        # Continuar com variáveis de ambiente
    
    # Usar variáveis de ambiente
    return {
        'region': REGION,
        'user_pool_id': COGNITO_USER_POOL_ID,
        'app_client_id': COGNITO_APP_CLIENT_ID
    }

def get_public_keys():
    """Obtém as chaves públicas do Cognito para verificação de tokens"""
    cognito_config = get_cognito_config()
    keys_url = f"https://cognito-idp.{cognito_config['region']}.amazonaws.com/{cognito_config['user_pool_id']}/.well-known/jwks.json"
    
    try:
        response = requests.get(keys_url)
        response.raise_for_status()
        return response.json()["keys"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao obter chaves públicas do Cognito: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível obter chaves de autenticação"
        )

# Inicializar chaves
keys = []
try:
    keys = get_public_keys()
except Exception as e:
    logger.warning(f"Não foi possível carregar chaves inicialmente: {str(e)}")
    # As chaves serão carregadas na primeira solicitação

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """Verifica o token JWT do Cognito"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido"
        )
    
    token = credentials.credentials
    # Log seguro sem expor token
    logger.debug("Token JWT recebido para validação")
    
    # Obter configuração do Cognito
    cognito_config = get_cognito_config()
    
    # Obter chaves se ainda não foram carregadas
    global keys
    if not keys:
        keys = get_public_keys()
    
    # Verificar headers do token
    try:
        headers = jwt.get_unverified_headers(token)
    except Exception as e:
        logger.error(f"Erro ao decodificar headers do token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    kid = headers.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem identificador de chave (kid)"
        )

    # Encontrar a chave correspondente
    key = next((k for k in keys if k["kid"] == kid), None)
    if key is None:
        # Tentar recarregar as chaves
        keys = get_public_keys()
        key = next((k for k in keys if k["kid"] == kid), None)
        if key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chave pública não encontrada"
            )

    # Verificar o token
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        
        # Construir a chave pública RSA
        n = base64url_decode(key["n"].encode("utf-8"))
        e = base64url_decode(key["e"].encode("utf-8"))

        public_numbers = rsa.RSAPublicNumbers(
            int.from_bytes(e, "big"),
            int.from_bytes(n, "big")
        )
        public_key = public_numbers.public_key(default_backend())

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Verificar token
        claims = jwt.decode(
            token,
            pem,
            algorithms=["RS256"],
            issuer=f"https://cognito-idp.{cognito_config['region']}.amazonaws.com/{cognito_config['user_pool_id']}",
            options={"verify_aud": False}  # Não verificar audience
        )

        logger.info(f"Token verificado com sucesso para usuário: {claims.get('email') or claims.get('cognito:username')}")
        return claims

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro nos claims: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro na verificação do token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Falha na autenticação: {str(e)}"
        )

def get_current_user(claims: dict = Depends(verify_token)):
    """Extrai informações do usuário a partir dos claims do token"""
    return {
        "username": claims.get("username") or claims.get("cognito:username"),
        "email": claims.get("email"),
        "groups": claims.get("cognito:groups", []),
        "sub": claims.get("sub")
    }
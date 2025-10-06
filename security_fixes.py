"""
🔒 Correções de Segurança para API ProjetoVida
Implementa melhorias de segurança baseadas na revisão
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os

# Configurar logger sem exposição de dados sensíveis
logger = logging.getLogger(__name__)

def setup_security_middleware(app: FastAPI):
    """Configura middlewares de segurança"""
    
    # 1. Rate Limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 2. CORS mais restritivo
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )
    
    # 3. Trusted Host
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )
    
    # 4. Headers de Segurança
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS apenas em produção
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    # 5. Logging seguro
    @app.middleware("http")
    async def secure_logging(request: Request, call_next):
        # Log sem exposição de dados sensíveis
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Verificar origem sem logar dados sensíveis
        origin = request.headers.get("Origin") or request.headers.get("Referer")
        if origin:
            logger.info(f"Origin: {origin}")
        
        # Verificar auth sem logar o token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            logger.info("Auth header presente")
        else:
            logger.warning(f"Requisição sem token: {request.url.path}")
        
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response

# Decorators para rate limiting
def rate_limit_pacientes():
    """Rate limit para operações de pacientes"""
    return limiter.limit("20/minute")

def rate_limit_auth():
    """Rate limit para autenticação"""
    return limiter.limit("5/minute")

def rate_limit_upload():
    """Rate limit para uploads"""
    return limiter.limit("10/hour")

# Validação de upload segura
from pydantic import BaseModel, validator
from typing import Optional
import base64

class SecureFileUpload(BaseModel):
    fileName: str
    fileType: str
    fileData: str
    
    @validator('fileName')
    def validate_file_name(cls, v):
        # Validar nome do arquivo
        if not v or len(v) > 255:
            raise ValueError('Nome de arquivo inválido')
        
        # Verificar caracteres perigosos
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Nome de arquivo contém caracteres inválidos')
        
        return v
    
    @validator('fileType')
    def validate_file_type(cls, v):
        allowed_types = [
            'image/jpeg',
            'image/png', 
            'image/gif',
            'application/pdf',
            'text/plain'
        ]
        if v not in allowed_types:
            raise ValueError('Tipo de arquivo não permitido')
        return v
    
    @validator('fileData')
    def validate_file_data(cls, v):
        try:
            # Decodificar base64 para verificar tamanho
            decoded = base64.b64decode(v)
            
            # Limite de 5MB
            max_size = 5 * 1024 * 1024
            if len(decoded) > max_size:
                raise ValueError('Arquivo muito grande (máximo 5MB)')
            
            # Verificar se é base64 válido
            base64.b64decode(v, validate=True)
            
        except Exception as e:
            raise ValueError('Dados de arquivo inválidos')
        
        return v

# Função para sanitizar logs
def sanitize_log_data(data: dict) -> dict:
    """Remove dados sensíveis dos logs"""
    sensitive_keys = ['password', 'token', 'secret', 'key', 'auth']
    sanitized = {}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
    
    return sanitized

# Configuração de logging seguro
def setup_secure_logging():
    """Configura logging sem exposição de dados sensíveis"""
    
    class SecureFormatter(logging.Formatter):
        def format(self, record):
            # Remover dados sensíveis do log
            if hasattr(record, 'args') and record.args:
                record.args = tuple(sanitize_log_data(arg) if isinstance(arg, dict) else arg 
                                  for arg in record.args)
            return super().format(record)
    
    # Configurar formatter
    formatter = SecureFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Aplicar a todos os handlers
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)

# Exemplo de uso nas rotas
"""
# Aplicar nas rotas principais:

@app.post("/pacientes/")
@rate_limit_pacientes()
def create_paciente(...):
    # Implementação
    pass

@app.post("/upload-mobile/{session_id}")
@rate_limit_upload()
async def upload_mobile(session_id: str, file_data: SecureFileUpload):
    # Implementação segura
    pass

@app.post("/auth/validate-token")
@rate_limit_auth()
async def validate_token(...):
    # Implementação
    pass
"""

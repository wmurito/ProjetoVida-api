import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import boto3
import json
import logging

logger = logging.getLogger(__name__)

class FieldEncryption:
    def __init__(self):
        self._cipher = None
        self._key = None
    
    def _get_encryption_key(self):
        """Obtém chave de criptografia do Secrets Manager ou gera uma"""
        if self._key:
            return self._key
        
        try:
            # Tentar obter do Secrets Manager em produção
            if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
                client = boto3.client('secretsmanager')
                response = client.get_secret_value(SecretId='projeto-vida/encryption-key')
                secret = json.loads(response['SecretString'])
                self._key = secret['key'].encode()
            else:
                # Desenvolvimento: usar variável de ambiente ou gerar
                key_str = os.getenv('ENCRYPTION_KEY')
                if not key_str:
                    # Gerar chave para desenvolvimento
                    self._key = Fernet.generate_key()
                    logger.warning("Usando chave de criptografia temporária para desenvolvimento")
                else:
                    self._key = key_str.encode()
        except Exception as e:
            logger.error(f"Erro ao obter chave de criptografia: {e}")
            # Fallback: gerar chave temporária
            self._key = Fernet.generate_key()
        
        return self._key
    
    def _get_cipher(self):
        """Obtém instância do cipher"""
        if not self._cipher:
            key = self._get_encryption_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def encrypt(self, value):
        """Criptografa um valor"""
        if not value:
            return None
        
        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erro ao criptografar: {e}")
            raise
    
    def decrypt(self, encrypted_value):
        """Descriptografa um valor"""
        if not encrypted_value:
            return None
        
        try:
            cipher = self._get_cipher()
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            return None

# Instância global
encryption = FieldEncryption()

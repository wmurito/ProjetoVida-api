"""
Módulo de segurança para criptografia e proteção de dados sensíveis
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class DataEncryption:
    """Classe para criptografia de dados sensíveis"""
    
    def __init__(self):
        # Usar chave do ambiente ou gerar uma nova
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Obtém ou cria chave de criptografia"""
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env.encode())
            except Exception as e:
                logger.warning(f"Chave de criptografia inválida: {e}")
        
        # Gerar nova chave se não existir
        key = Fernet.generate_key()
        logger.warning("Nova chave de criptografia gerada. Configure ENCRYPTION_KEY no ambiente.")
        return key
    
    def encrypt_cpf(self, cpf: str) -> str:
        """Criptografa CPF"""
        if not cpf:
            return ""
        
        # Limpar CPF (remover pontos, traços, espaços)
        clean_cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(clean_cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        
        encrypted = self.cipher.encrypt(clean_cpf.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_cpf(self, encrypted_cpf: str) -> str:
        """Descriptografa CPF"""
        if not encrypted_cpf:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_cpf.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar CPF: {e}")
            raise ValueError("CPF criptografado inválido")
    
    def hash_sensitive_data(self, data: str) -> str:
        """Cria hash seguro para dados sensíveis"""
        if not data:
            return ""
        
        # Usar salt do ambiente
        salt = os.getenv('HASH_SALT', 'default_salt_change_in_production').encode()
        
        # Criar hash com PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(data.encode()))
        return key.decode()

class InputSanitizer:
    """Classe para sanitização de entrada"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitiza string removendo caracteres perigosos"""
        if not value:
            return ""
        
        # Remover caracteres de controle e perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        # Limitar tamanho
        return value[:max_length].strip()
    
    @staticmethod
    def validate_cpf_format(cpf: str) -> bool:
        """Valida formato do CPF"""
        if not cpf:
            return False
        
        # Remover caracteres não numéricos
        clean_cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se tem 11 dígitos
        if len(clean_cpf) != 11:
            return False
        
        # Verificar se não são todos iguais
        if clean_cpf == clean_cpf[0] * 11:
            return False
        
        return True
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Valida formato do email"""
        if not email:
            return False
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

class SecurityHeaders:
    """Classe para cabeçalhos de segurança"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Retorna cabeçalhos de segurança recomendados"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }

# Instâncias globais
encryption = DataEncryption()
sanitizer = InputSanitizer()
security_headers = SecurityHeaders()

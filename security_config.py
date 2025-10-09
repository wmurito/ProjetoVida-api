"""
Configurações de segurança para o ProjetoVida API
"""
import os
from typing import List

class SecurityConfig:
    """Configurações centralizadas de segurança"""
    
    # Rate Limiting
    RATE_LIMIT_AUTH = "5/minute"
    RATE_LIMIT_UPLOAD = "3/minute"
    RATE_LIMIT_SESSION = "5/minute"
    RATE_LIMIT_STATUS = "30/minute"
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = 2
    MAX_UPLOADS_PER_SESSION = 3
    
    # File Upload
    MAX_FILE_SIZE_MB = 2
    ALLOWED_FILE_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/jpg'
    ]
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']
    
    # CORS
    CORS_MAX_AGE = 1800  # 30 minutos
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    HASH_SALT = os.getenv('HASH_SALT', 'default_salt_change_in_production')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_SENSITIVE_DATA = False
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Suspicious User Agents
    SUSPICIOUS_USER_AGENTS = [
        "bot", "crawler", "scanner", "sqlmap", "nikto", "nmap",
        "masscan", "zap", "burp", "w3af", "acunetix"
    ]
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Retorna origens permitidas de forma segura"""
        origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://192.168.2.101:5173"
        ).split(",")
        
        # Filtrar origens perigosas
        safe_origins = []
        for origin in origins:
            origin = origin.strip()
            if origin and not origin.startswith('*'):
                safe_origins.append(origin)
        
        return safe_origins
    
    @classmethod
    def is_production(cls) -> bool:
        """Verifica se está em ambiente de produção"""
        return bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Retorna origens CORS apropriadas para o ambiente"""
        if cls.is_production():
            # Em produção, usar domínio específico da API Gateway
            return ["https://84i8-3.execute-api.us-east-1.amazonaws.com"]
        else:
            return cls.get_allowed_origins()

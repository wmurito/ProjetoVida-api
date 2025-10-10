import logging
import re

class SecureLogger:
    """Logger que sanitiza dados sensíveis antes de registrar"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.sensitive_patterns = [
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]'),  # Email
            (r'\(\d{2}\)\s?\d{4,5}-\d{4}', '[PHONE]'),  # Telefone
            (r'"password"\s*:\s*"[^"]*"', '"password":"[REDACTED]"'),  # Password em JSON
            (r'"token"\s*:\s*"[^"]*"', '"token":"[REDACTED]"'),  # Token em JSON
            (r'Bearer\s+[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*', 'Bearer [TOKEN]'),  # JWT
        ]
    
    def _sanitize(self, message):
        """Remove dados sensíveis da mensagem"""
        if not isinstance(message, str):
            message = str(message)
        
        for pattern, replacement in self.sensitive_patterns:
            message = re.sub(pattern, replacement, message)
        
        return message
    
    def debug(self, message, *args, **kwargs):
        self.logger.debug(self._sanitize(message), *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        self.logger.info(self._sanitize(message), *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self.logger.warning(self._sanitize(message), *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self.logger.error(self._sanitize(message), *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        self.logger.critical(self._sanitize(message), *args, **kwargs)

# Função helper para criar logger seguro
def get_secure_logger(name):
    return SecureLogger(name)

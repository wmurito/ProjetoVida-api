"""
🔒 Correções de Segurança para Sistema de Upload via QR Code
Implementa melhorias de segurança baseadas na análise
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import base64
import uuid
import hashlib
import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

# Configurar logger seguro
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Armazenamento de sessões (em produção, usar Redis)
active_sessions: Dict[str, Dict] = {}

class SecureFileUpload(BaseModel):
    """Validação segura de upload de arquivo"""
    fileName: str
    fileType: str
    fileData: str
    
    @validator('fileName')
    def validate_file_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Nome de arquivo inválido')
        
        # Verificar caracteres perigosos
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Nome de arquivo contém caracteres inválidos')
        
        # Verificar extensão
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError('Extensão de arquivo não permitida')
        
        return v
    
    @validator('fileType')
    def validate_file_type(cls, v):
        allowed_types = [
            'application/pdf',
            'image/jpeg', 
            'image/png'
        ]
        if v not in allowed_types:
            raise ValueError('Tipo de arquivo não permitido')
        return v
    
    @validator('fileData')
    def validate_file_data(cls, v):
        try:
            # Verificar se é base64 válido
            if not v.startswith('data:'):
                raise ValueError('Formato de dados inválido')
            
            # Extrair dados base64
            header, data = v.split(',', 1)
            decoded = base64.b64decode(data)
            
            # Limite de 5MB
            max_size = 5 * 1024 * 1024
            if len(decoded) > max_size:
                raise ValueError('Arquivo muito grande (máximo 5MB)')
            
            # Verificar se é base64 válido
            base64.b64decode(data, validate=True)
            
        except Exception as e:
            raise ValueError(f'Dados de arquivo inválidos: {str(e)}')
        
        return v

class SessionManager:
    """Gerenciador de sessões seguro"""
    
    @staticmethod
    def create_session(ip_address: str) -> str:
        """Cria uma nova sessão segura"""
        session_id = f"upload-{uuid.uuid4()}"
        
        active_sessions[session_id] = {
            'created_at': datetime.utcnow(),
            'ip_address': ip_address,
            'uploads_count': 0,
            'last_activity': datetime.utcnow()
        }
        
        logger.info(f"Sessão criada: {session_id[:8]}...")
        return session_id
    
    @staticmethod
    def validate_session(session_id: str, ip_address: str) -> bool:
        """Valida se a sessão é válida"""
        if session_id not in active_sessions:
            return False
        
        session = active_sessions[session_id]
        
        # Verificar expiração (5 minutos)
        if datetime.utcnow() - session['created_at'] > timedelta(minutes=5):
            del active_sessions[session_id]
            return False
        
        # Verificar IP (opcional, pode ser restritivo)
        # if session['ip_address'] != ip_address:
        #     return False
        
        # Atualizar última atividade
        session['last_activity'] = datetime.utcnow()
        
        return True
    
    @staticmethod
    def increment_upload_count(session_id: str):
        """Incrementa contador de uploads"""
        if session_id in active_sessions:
            active_sessions[session_id]['uploads_count'] += 1
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove sessões expiradas"""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, session in active_sessions.items()
            if now - session['created_at'] > timedelta(minutes=5)
        ]
        
        for sid in expired_sessions:
            del active_sessions[sid]
        
        if expired_sessions:
            logger.info(f"Removidas {len(expired_sessions)} sessões expiradas")

# Função para sanitizar logs
def sanitize_log_data(data: dict) -> dict:
    """Remove dados sensíveis dos logs"""
    sensitive_keys = ['fileData', 'base64Data', 'password', 'token']
    sanitized = {}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
    
    return sanitized

# Endpoints seguros
def setup_secure_upload_routes(app: FastAPI):
    """Configura rotas de upload seguras"""
    
    # Rate limiting para uploads
    @app.post("/upload-mobile/{session_id}")
    @limiter.limit("5/minute")  # 5 uploads por minuto por IP
    async def secure_upload_mobile(
        session_id: str,
        file_data: SecureFileUpload,
        request: Request
    ):
        """Endpoint seguro para upload via mobile"""
        try:
            # Validar sessão
            if not SessionManager.validate_session(session_id, request.client.host):
                logger.warning(f"Tentativa de upload com sessão inválida: {session_id[:8]}...")
                raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
            
            # Incrementar contador de uploads
            SessionManager.increment_upload_count(session_id)
            
            # Log seguro (sem dados sensíveis)
            log_data = sanitize_log_data(file_data.dict())
            logger.info(f"Upload recebido: {log_data}")
            
            # Salvar no S3 (implementar conforme necessário)
            from s3_service import s3_service
            s3_service.save_upload(session_id, file_data.dict())
            
            return {"success": True, "message": "Arquivo recebido com sucesso"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro no upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    # Endpoint para verificar status
    @app.get("/upload-status/{session_id}")
    @limiter.limit("10/minute")  # 10 verificações por minuto
    async def secure_check_upload_status(
        session_id: str,
        request: Request
    ):
        """Endpoint seguro para verificar status do upload"""
        try:
            # Validar sessão
            if not SessionManager.validate_session(session_id, request.client.host):
                raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
            
            # Buscar arquivo no S3
            from s3_service import s3_service
            data = s3_service.get_upload(session_id)
            
            if data:
                # Log seguro
                log_data = sanitize_log_data(data)
                logger.info(f"Arquivo encontrado: {log_data}")
                return data
            else:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    # Endpoint para criar sessão
    @app.post("/create-upload-session")
    @limiter.limit("10/minute")  # 10 sessões por minuto
    async def create_upload_session(request: Request):
        """Cria uma nova sessão de upload"""
        try:
            session_id = SessionManager.create_session(request.client.host)
            
            # Limpar sessões expiradas
            SessionManager.cleanup_expired_sessions()
            
            return {
                "session_id": session_id,
                "upload_url": f"/upload-mobile/{session_id}",
                "expires_in": 300  # 5 minutos
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    # Endpoint para limpar sessões expiradas
    @app.post("/cleanup-sessions")
    async def cleanup_sessions():
        """Limpa sessões expiradas"""
        try:
            SessionManager.cleanup_expired_sessions()
            return {"message": "Sessões expiradas removidas"}
        except Exception as e:
            logger.error(f"Erro ao limpar sessões: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Middleware de segurança
def setup_upload_security_middleware(app: FastAPI):
    """Configura middlewares de segurança para upload"""
    
    # Rate limiting global
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Middleware para log de uploads
    @app.middleware("http")
    async def upload_logging_middleware(request: Request, call_next):
        # Log de requisições de upload
        if "/upload-mobile/" in str(request.url):
            logger.info(f"Upload request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log de resposta
        if "/upload-mobile/" in str(request.url):
            logger.info(f"Upload response: {response.status_code}")
        
        return response
    
    # Middleware para limpeza de sessões
    @app.middleware("http")
    async def session_cleanup_middleware(request: Request, call_next):
        # Limpar sessões expiradas a cada 100 requisições
        if hasattr(request.state, 'request_count'):
            request.state.request_count += 1
        else:
            request.state.request_count = 1
        
        if request.state.request_count % 100 == 0:
            SessionManager.cleanup_expired_sessions()
        
        response = await call_next(request)
        return response

# Função para configurar tudo
def configure_secure_upload(app: FastAPI):
    """Configura sistema de upload seguro"""
    setup_upload_security_middleware(app)
    setup_secure_upload_routes(app)
    
    logger.info("Sistema de upload seguro configurado")

# Exemplo de uso no main.py:
"""
from upload_security_fixes import configure_secure_upload

# No main.py, após criar a app:
configure_secure_upload(app)
"""

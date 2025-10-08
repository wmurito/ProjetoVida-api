# Versão otimizada do main.py para AWS Lambda
# Resolve problemas de importação e otimiza para baixo custo

import os
import logging
from typing import List, Dict, Any

# Configurar logging otimizado para Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração para ambiente AWS Lambda
stage = os.environ.get('STAGE', 'prod')
root_path = f"/{stage}" if stage else ""

# Importações otimizadas (lazy loading para reduzir cold start)
def get_fastapi_app():
    """Cria a aplicação FastAPI com configurações otimizadas"""
    from fastapi import FastAPI, Depends, HTTPException, Request, status
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    
    # Importações locais
    import crud, models, schemas
    from database import SessionLocal, engine
    from auth import verify_token, get_current_user
    from dashboard import (
        get_estadiamento, 
        get_sobrevida_global, 
        get_taxa_recidiva, 
        get_media_delta_t
    )
    from s3_service import s3_service
    
    # Criar tabelas no banco de dados (apenas se necessário)
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados verificadas/criadas")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
    
    # Inicializar FastAPI com configuração otimizada para Lambda
    app = FastAPI(
        title="API Projeto Vida - Otimizada",
        description="API otimizada para cadastro de pacientes oncológicos",
        version="2.0.0",
        root_path=root_path,
        docs_url="/docs" if stage != "prod" else None,  # Docs apenas em dev
        redoc_url="/redoc" if stage != "prod" else None
    )
    
    # Configurar CORS otimizado
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Dependência para obter sessão do banco de dados
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Middleware otimizado para log de requisições
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = os.times()
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log apenas em caso de erro ou para monitoramento
        if response.status_code >= 400:
            logger.warning(f"Response status: {response.status_code}")
        
        return response
    
    # ===== ROTAS OTIMIZADAS =====
    
    # Rota raiz (pública)
    @app.get("/")
    def read_root():
        return {
            "message": "API Projeto Vida - Otimizada",
            "version": "2.0.0",
            "stage": stage,
            "status": "active"
        }
    
    # Rota de teste otimizada
    @app.get("/test")
    def test_api():
        try:
            # Teste básico de conectividade
            db = SessionLocal()
            result = db.execute(text("SELECT 1"))
            db.close()
            
            return {
                "status": "success",
                "message": "API funcionando corretamente",
                "database": "conectado",
                "stage": stage
            }
        except Exception as e:
            logger.error(f"Erro no teste da API: {e}")
            return {
                "status": "error",
                "message": f"Erro na API: {str(e)}"
            }
    
    # Rota de verificação de autenticação
    @app.get("/auth/me", response_model=Dict[str, Any])
    def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
        return current_user
    
    # ===== ROTAS DE PACIENTES (OTIMIZADAS) =====
    
    @app.post("/pacientes/", response_model=schemas.Paciente)
    def create_paciente(
        paciente: schemas.PacienteCreate, 
        db: Session = Depends(get_db),
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        return crud.create_paciente(db=db, paciente=paciente)
    
    @app.get("/pacientes/", response_model=List[schemas.Paciente])
    def read_pacientes(
        skip: int = 0, 
        limit: int = 100, 
        db: Session = Depends(get_db),
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        return crud.get_pacientes(db, skip=skip, limit=limit)
    
    @app.get("/pacientes/{paciente_id}", response_model=schemas.Paciente)
    def read_paciente(
        paciente_id: int, 
        db: Session = Depends(get_db),
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        db_paciente = crud.get_paciente(db, paciente_id=paciente_id)
        if db_paciente is None:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return db_paciente
    
    @app.put("/pacientes/{paciente_id}", response_model=schemas.Paciente)
    def update_paciente(
        paciente_id: int, 
        paciente: schemas.PacienteCreate, 
        db: Session = Depends(get_db),
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        db_paciente = crud.update_paciente(db, paciente_id=paciente_id, paciente=paciente)
        if db_paciente is None:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return db_paciente
    
    @app.delete("/pacientes/{paciente_id}")
    def delete_paciente(
        paciente_id: int, 
        db: Session = Depends(get_db),
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        deleted = crud.delete_paciente(db, paciente_id=paciente_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return {"ok": True}
    
    # ===== ROTAS DO DASHBOARD (OTIMIZADAS) =====
    
    @app.get("/dashboard/estadiamento")
    def dashboard_estadiamento(
        db: Session = Depends(get_db), 
        current_user: dict = Depends(get_current_user)
    ):
        return get_estadiamento(db)
    
    @app.get("/dashboard/sobrevida")
    def dashboard_sobrevida(
        db: Session = Depends(get_db), 
        current_user: dict = Depends(get_current_user)
    ):
        return get_sobrevida_global(db)
    
    @app.get("/dashboard/recidiva")
    def dashboard_recidiva(
        db: Session = Depends(get_db), 
        current_user: dict = Depends(get_current_user)
    ):
        return get_taxa_recidiva(db)
    
    @app.get("/dashboard/delta_t")
    def dashboard_delta_t(
        db: Session = Depends(get_db), 
        current_user: dict = Depends(get_current_user)
    ):
        return get_media_delta_t(db)
    
    # ===== ROTAS DE UPLOAD SEGURO (OTIMIZADAS) =====
    
    # Importações para upload (lazy loading)
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    import uuid
    import base64
    from datetime import datetime, timedelta
    from pydantic import BaseModel, validator
    
    # Rate limiter otimizado
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
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
                'image/png',
                'image/jpg'
            ]
            if v not in allowed_types:
                raise ValueError('Tipo de arquivo não permitido')
            return v
        
        @validator('fileData')
        def validate_file_data(cls, v):
            try:
                if not v.startswith('data:'):
                    raise ValueError('Formato de dados inválido')
                
                header, data = v.split(',', 1)
                decoded = base64.b64decode(data)
                
                # Limite de 5MB
                max_size = 5 * 1024 * 1024
                if len(decoded) > max_size:
                    raise ValueError('Arquivo muito grande (máximo 5MB)')
                
                base64.b64decode(data, validate=True)
                
            except Exception as e:
                raise ValueError(f'Dados de arquivo inválidos: {str(e)}')
            
            return v
    
    def validate_session(session_id: str, ip_address: str) -> bool:
        """Valida se a sessão é válida"""
        if session_id not in active_sessions:
            return False
        
        session = active_sessions[session_id]
        
        # Verificar expiração (5 minutos)
        if datetime.utcnow() - session['created_at'] > timedelta(minutes=5):
            del active_sessions[session_id]
            return False
        
        # Atualizar última atividade
        session['last_activity'] = datetime.utcnow()
        return True
    
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
    
    @app.post("/upload-mobile/{session_id}")
    @limiter.limit("5/minute")
    async def secure_upload_mobile(
        session_id: str,
        file_data: SecureFileUpload,
        request: Request
    ):
        """Endpoint seguro para upload via mobile"""
        try:
            if not validate_session(session_id, request.client.host):
                logger.warning(f"Tentativa de upload com sessão inválida: {session_id[:8]}...")
                raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
            
            if session_id in active_sessions:
                active_sessions[session_id]['uploads_count'] += 1
            
            logger.info(f"Upload recebido para sessão: {session_id[:8]}...")
            
            # Salvar no S3
            s3_service.save_upload(session_id, file_data.dict())
            
            return {"success": True, "message": "Arquivo recebido com sucesso"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro no upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    @app.get("/upload-status/{session_id}")
    @limiter.limit("60/minute")
    async def secure_check_upload_status(
        session_id: str,
        request: Request
    ):
        """Endpoint seguro para verificar status do upload"""
        try:
            if not validate_session(session_id, request.client.host):
                raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
            
            data = s3_service.get_upload(session_id)
            
            if data:
                logger.info(f"Arquivo encontrado para sessão: {session_id[:8]}...")
                return data
            else:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    @app.post("/create-upload-session")
    @limiter.limit("10/minute")
    async def create_upload_session(request: Request):
        """Cria uma nova sessão de upload"""
        try:
            session_id = create_session(request.client.host)
            
            # Limpar sessões expiradas
            now = datetime.utcnow()
            expired_sessions = [
                sid for sid, session in active_sessions.items()
                if now - session['created_at'] > timedelta(minutes=5)
            ]
            
            for sid in expired_sessions:
                del active_sessions[sid]
            
            return {
                "session_id": session_id,
                "upload_url": f"/upload-mobile/{session_id}",
                "expires_in": 300
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
    return app

# Criar a aplicação
app = get_fastapi_app()

# Handler para AWS Lambda (otimizado)
from mangum import Mangum
handler = Mangum(app, lifespan="off")  # Desabilitar lifespan para melhor performance

# Função para desenvolvimento local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

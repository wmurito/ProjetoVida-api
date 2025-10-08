from fastapi import FastAPI, Depends, HTTPException, Request, status, Body
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import crud, models, schemas
from database import SessionLocal, engine
import os

# Configuração temporária para desenvolvimento com SQLite
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./projetovida_dev.db"
from mangum import Mangum
from typing import List, Dict, Any, Tuple
import exportar #
import os
import logging
from auth import verify_token, get_current_user
from dashboard import ( get_estadiamento, get_sobrevida_global, get_taxa_recidiva, get_media_delta_t)
from s3_service import s3_service
# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração para ambiente AWS Lambda
stage = os.environ.get('STAGE', None)
root_path = f"/{stage}" if stage else ""

# Criar tabelas apenas em desenvolvimento local
if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI com configuração para Lambda
app = FastAPI(
    title="API de Formulário de Pacientes",
    description="API para gerenciamento de formulários de pacientes oncológicos",
    version="1.0.0",
    root_path=root_path
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.2.101:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handler para AWS Lambda
handler = Mangum(app)

# Dependência para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log detalhado dos cabeçalhos
    logger.info(f"Request: {request.method} {request.url}")
    
    # Verificar origem da requisição
    origin = request.headers.get("Origin") or request.headers.get("Referer")
    if origin:
        logger.info(f"Origem da requisição: {origin}")
    
    # Verificar cabeçalho de autorização
    auth_header = request.headers.get("Authorization")
    if auth_header:
        logger.info(f"Auth header presente: {auth_header[:30]}...")
    else:
        logger.info("Auth header ausente")
        
        # Se for uma requisição do frontend, adicionar um log mais detalhado
        if origin and "localhost:5173" in origin:
            logger.warning(f"Requisição do frontend sem token: {request.url}")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Rota raiz (pública)
@app.get("/")
def read_root():
    return {"message": "API de Formulário de Pacientes"}

# Rota de teste para verificar se a API está funcionando
@app.get("/test")
def test_api():
    try:
        # Testar conexão com banco
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "success",
            "message": "API funcionando corretamente",
            "database": "conectado",
            "models": "atualizados"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na API: {str(e)}"
        }

# Rota de verificação de autenticação
@app.get("/auth/me", response_model=Dict[str, Any])
def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    logger.info(f"Usuário autenticado: {current_user}")
    return current_user

# Rota de teste para debug de autenticação
@app.get("/auth/test")
def test_auth(request: Request):
    auth_header = request.headers.get("Authorization")
    logger.info(f"Headers na rota de teste: {request.headers}")
    if auth_header:
        return {"status": "ok", "auth_header": auth_header[:20] + "..."}
    else:
        return {"status": "error", "message": "Cabeçalho de autorização ausente"}

# Rota de teste para pacientes sem autenticação
@app.get("/pacientes/teste")
def test_pacientes():
    return {"message": "Rota de teste para pacientes funcionando"}

@app.get('/api/pacientes/exportar_excel')
def api_exportar_pacientes_excel():
    print("Requisição para exportar pacientes para Excel recebida.")
    
    # Chama a função do seu script exportar.py
    filepath = exportar.gerar_relatorio_pacientes_excel()
    
    if filepath:
        try:
            # Serve o arquivo para download
            filename = os.path.basename(filepath)
            
            print(f"Enviando arquivo: {filename}")
            
            # Função para remover o arquivo após o envio
            def remove_file():
                try:
                    os.remove(filepath)
                    print(f"Arquivo temporário {filepath} removido.")
                except Exception as error:
                    print(f"Erro ao remover arquivo temporário {filepath}: {error}")
            
            # Retorna o arquivo e configura para removê-lo após o envio
            return FileResponse(
                path=filepath, 
                filename=filename, 
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                background=BackgroundTask(remove_file)
            )
        except Exception as e:
            print(f"Erro ao enviar o arquivo {filepath}: {e}")
            return JSONResponse(
                content={"error": "Erro ao preparar o arquivo para download."}, 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return JSONResponse(
            content={"error": "Falha ao gerar o relatório Excel."}, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Rota para testar autenticação com token
@app.post("/auth/validate-token")
async def validate_token(request: Request):
    try:
        body = await request.json()
        token = body.get("token")
        if not token:
            return {"valid": False, "error": "Token não fornecido"}
        
        # Log do token recebido
        logger.info(f"Token recebido para validação: {token[:20]}...")
        
        # Tentar validar o token manualmente
        from auth import verify_token
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Criar credenciais manualmente
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        try:
            # Tentar verificar o token
            claims = await verify_token(credentials)
            return {"valid": True, "claims": claims}
        except Exception as e:
            logger.error(f"Erro ao validar token: {str(e)}")
            return {"valid": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
        return {"valid": False, "error": str(e)}

# Rotas protegidas para Paciente
@app.post("/pacientes/", response_model=schemas.Paciente)
def create_paciente(
    paciente: schemas.PacienteCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return crud.create_paciente(db=db, paciente=paciente)

# Rota para visualização detalhada do paciente
@app.get("/paciente/view/{paciente_id}")
def get_paciente_view(paciente_id: int, db: Session = Depends(get_db)):
    paciente = crud.get_paciente_detalhes(db, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@app.get("/pacientes/", response_model=List[schemas.Paciente])
def read_pacientes(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Log detalhado dos cabeçalhos para debug
    logger.info(f"Headers na rota pacientes: {request.headers}")
    logger.info(f"Usuário autenticado: {current_user}")
    pacientes = crud.get_pacientes(db, skip=skip, limit=limit)
    return pacientes

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

# Rota para histórico (protegida)
@app.get("/pacientes/{paciente_id}/historico")
def read_paciente_historico(
    paciente_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retorna o histórico de alterações de um paciente específico"""
    historico = db.query(models.PacienteHistorico).filter(
        models.PacienteHistorico.paciente_id == paciente_id
    ).order_by(models.PacienteHistorico.data_modificacao.desc()).all()
    
    # Converter para formato adequado para frontend
    resultado = []
    for h in historico:
        resultado.append({
            "id": h.id,
            "paciente_id": h.paciente_id,
            "data_modificacao": h.data_modificacao,
            "dados_anteriores": h.dados_anteriores
        })
    
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


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

# Endpoints seguros para upload via QR Code
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid
import base64
from datetime import datetime, timedelta
from pydantic import BaseModel, validator

# Rate limiter
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
            'image/jpg'  # Adicionar suporte para image/jpg
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
@limiter.limit("5/minute")  # 5 uploads por minuto por IP
async def secure_upload_mobile(
    session_id: str,
    file_data: SecureFileUpload,
    request: Request
):
    """Endpoint seguro para upload via mobile"""
    try:
        # Validar sessão
        if not validate_session(session_id, request.client.host):
            logger.warning(f"Tentativa de upload com sessão inválida: {session_id[:8]}...")
            raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
        
        # Incrementar contador de uploads
        if session_id in active_sessions:
            active_sessions[session_id]['uploads_count'] += 1
        
        # Log seguro (sem dados sensíveis)
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
@limiter.limit("60/minute")  # 60 verificações por minuto (1 por segundo)
async def secure_check_upload_status(
    session_id: str,
    request: Request
):
    """Endpoint seguro para verificar status do upload"""
    try:
        # Validar sessão
        if not validate_session(session_id, request.client.host):
            raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
        
        # Buscar arquivo no S3
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
@limiter.limit("10/minute")  # 10 sessões por minuto
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
            "expires_in": 300  # 5 minutos
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

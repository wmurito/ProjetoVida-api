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
import exportar
import os
from secure_logger import get_secure_logger
from auth import verify_token, get_current_user
from dashboard import ( get_estadiamento, get_sobrevida_global, get_taxa_recidiva, get_media_delta_t)
from s3_service import s3_service
# Configurar logging seguro
logger = get_secure_logger(__name__)

# Criar tabelas apenas em desenvolvimento local
if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="ProjetoVida API",
    description="API segura para gerenciamento de pacientes oncológicos",
    version="1.0.0"
)

# Configurar CORS seguro
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://192.168.2.101:5173,https://master.d1yi28nqqe44f2.amplifyapp.com"
).split(",")

# Validar origens para evitar configurações perigosas
def validate_origins(origins):
    """Valida se as origens são seguras"""
    safe_origins = []
    for origin in origins:
        origin = origin.strip()
        if origin and not origin.startswith('*'):
            safe_origins.append(origin)
    return safe_origins

SAFE_ORIGINS = validate_origins(ALLOWED_ORIGINS)

# Em produção Lambda, adicionar origem do Amplify
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    SAFE_ORIGINS = ["https://master.d1yi28nqqe44f2.amplifyapp.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=SAFE_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
    max_age=1800,
    expose_headers=["X-Total-Count"]
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

# Middleware para log e segurança
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Log seguro sem dados sensíveis
    client_ip = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "")
    
    # Validar CSRF token para requisições que modificam dados
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or len(csrf_token) != 32:
            logger.warning("CSRF token inválido ou ausente")
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token inválido"}
            )
    
    # Para requisições OPTIONS (preflight), permitir passagem
    if request.method == "OPTIONS":
        # Validar origem para OPTIONS
        if origin and origin not in SAFE_ORIGINS:
            logger.warning(f"Origem não autorizada bloqueada para OPTIONS: {origin}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Origem não autorizada"},
                headers={
                    "Access-Control-Allow-Origin": "",
                }
            )
        
        # Permitir que OPTIONS passe para o CORS middleware
        response = await call_next(request)
        
        # Adicionar cabeçalhos de segurança para OPTIONS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
    
    # Para outras requisições, validar origem
    if origin and origin not in SAFE_ORIGINS:
        logger.warning(f"Origem não autorizada bloqueada: {origin}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Origem não autorizada"},
            headers={
                "Access-Control-Allow-Origin": "",
            }
        )
    
    # Verificar User-Agent suspeito
    user_agent = request.headers.get("user-agent", "")
    if any(suspicious in user_agent.lower() for suspicious in ["bot", "crawler", "scanner", "sqlmap"]):
        logger.warning(f"Request suspeito bloqueado: {user_agent[:50]}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Acesso negado"}
        )
    
    response = await call_next(request)
    
    # Adicionar cabeçalhos de segurança
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Rota raiz (pública - apenas status)
@app.get("/")
def read_root():
    return {"status": "online"}

# Rota para lidar com requisições OPTIONS (preflight CORS)
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """Handler para requisições OPTIONS (preflight CORS)"""
    origin = request.headers.get("origin", "")
    
    # Verificar se a origem é permitida
    if origin and origin in SAFE_ORIGINS:
        allow_origin = origin
    else:
        allow_origin = SAFE_ORIGINS[0] if SAFE_ORIGINS else "*"
    
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-CSRF-Token",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "1800"
        }
    )

# Rota de verificação de autenticação
@app.get("/auth/me", response_model=Dict[str, Any])
def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user



@app.get('/api/pacientes/exportar_excel')
def api_exportar_pacientes_excel(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    filepath = exportar.gerar_relatorio_pacientes_excel()
    
    if filepath:
        try:
            filename = os.path.basename(filepath)
            
            def remove_file():
                try:
                    os.remove(filepath)
                except Exception as error:
                    logger.error(f"Erro ao remover arquivo: {error}")
            
            return FileResponse(
                path=filepath, 
                filename=filename, 
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                background=BackgroundTask(remove_file)
            )
        except Exception as e:
            logger.error(f"Erro ao enviar arquivo: {e}")
            raise HTTPException(status_code=500, detail="Erro ao preparar arquivo")
    else:
        raise HTTPException(status_code=500, detail="Falha ao gerar relatório")

# Rate limiter e imports para upload
from fastapi import File, UploadFile, Form
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid
import base64
from datetime import datetime, timedelta
from pydantic import BaseModel, validator

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rota para testar autenticação com token (PROTEGIDA)
@app.post("/auth/validate-token")
@limiter.limit("5/minute")  # Rate limiting rigoroso
async def validate_token(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint protegido para validação de token.
    Apenas usuários autenticados podem validar tokens.
    """
    try:
        body = await request.json()
        token = body.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token não fornecido")
        
        # Validar formato do token
        if not token.startswith("Bearer "):
            token = f"Bearer {token}"
        
        from auth import verify_token
        from fastapi.security import HTTPAuthorizationCredentials
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token.replace("Bearer ", ""))
        
        try:
            claims = await verify_token(credentials)
            # Log de validação de token sanitizado
            return {"valid": True, "user": claims.get("email", "N/A")[:3] + "***"}
        except Exception as e:
            # Log de tentativa de validação inválida
            raise HTTPException(status_code=401, detail="Token inválido")
    except HTTPException:
        raise
    except Exception as e:
        # Log de erro de validação sanitizado
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Armazenamento de sessões seguro com TTL
import threading
from collections import defaultdict
from datetime import datetime, timedelta

# Thread-safe storage para sessões
active_sessions: Dict[str, Dict] = {}
session_lock = threading.Lock()

class SecureFileUpload(BaseModel):
    """Validação segura de upload de arquivo"""
    fileName: str
    fileType: str
    fileData: str
    prontuario: str
    
    @validator('fileName')
    def validate_file_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Nome de arquivo inválido')
        
        # Verificar caracteres perigosos
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*', ';', '&', '`', '$']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Nome de arquivo contém caracteres inválidos')
        
        # Verificar extensão
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError('Extensão de arquivo não permitida')
        
        # Verificar se não é um caminho absoluto
        if v.startswith('/') or v.startswith('\\'):
            raise ValueError('Nome de arquivo não pode ser um caminho absoluto')
        
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
            
            # Verificar tamanho (2MB máximo para maior segurança)
            max_size = 2 * 1024 * 1024
            if len(decoded) > max_size:
                raise ValueError('Arquivo muito grande (máximo 2MB)')
            
            # Verificar se é base64 válido
            base64.b64decode(data, validate=True)
            
            # Verificar assinatura de arquivo (magic bytes)
            if decoded.startswith(b'%PDF'):
                # PDF válido
                pass
            elif decoded.startswith(b'\xff\xd8\xff'):
                # JPEG válido
                pass
            elif decoded.startswith(b'\x89PNG\r\n\x1a\n'):
                # PNG válido
                pass
            else:
                raise ValueError('Tipo de arquivo não reconhecido ou corrompido')
            
        except Exception as e:
            raise ValueError(f'Dados de arquivo inválidos: {str(e)}')
        
        return v
    


def validate_session(session_id: str, ip_address: str) -> bool:
    """Valida se a sessão é válida com thread safety"""
    with session_lock:
        if session_id not in active_sessions:
            return False
        
        session = active_sessions[session_id]
        
        # Verificar expiração (2 minutos para maior segurança)
        if datetime.utcnow() - session['created_at'] > timedelta(minutes=2):
            del active_sessions[session_id]
            # Log de sessão expirada removida
            return False
        
        # Verificar IP address
        if session.get('ip_address') != ip_address:
            logger.warning(f"Tentativa de acesso com IP diferente: {session_id[:8]}...")
            del active_sessions[session_id]
            return False
        
        session['last_activity'] = datetime.utcnow()
        return True

def create_session(ip_address: str) -> str:
    """Cria uma nova sessão segura com thread safety"""
    session_id = f"upload-{uuid.uuid4()}"
    
    with session_lock:
        active_sessions[session_id] = {
            'created_at': datetime.utcnow(),
            'ip_address': ip_address,
            'uploads_count': 0,
            'last_activity': datetime.utcnow(),
            'max_uploads': 3  # Limite de uploads por sessão
        }
    
    logger.info(f"Sessão segura criada: {session_id[:8]}... para IP: {ip_address[:8]}***")
    return session_id

# Rotas protegidas para Paciente

@app.post("/upload-termo-aceite")
@limiter.limit("5/minute")
async def upload_termo_aceite(
    prontuario: str = Form(...),
    termo: UploadFile = File(...),
    request: Request = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Endpoint para upload do termo de aceite via desktop"""
    try:
        # Validar prontuário
        if not prontuario or len(prontuario) < 3:
            raise HTTPException(status_code=400, detail="Prontuário inválido")
        
        # Ler conteúdo do arquivo
        content = await termo.read()
        
        # Validar tamanho (5MB)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 5MB")
        
        # Validar tipo de arquivo pelo conteúdo (magic bytes)
        if content.startswith(b'%PDF'):
            file_type = 'application/pdf'
        elif content.startswith(b'\xff\xd8\xff'):
            file_type = 'image/jpeg'
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            file_type = 'image/png'
        else:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido. Use PDF, JPG ou PNG")
        
        # Validar content-type declarado
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if termo.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Content-Type não permitido")
        
        # Salvar no S3
        termo_key = f"termos/{prontuario}/termo_aceite.pdf"
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket,
            Key=termo_key,
            Body=content,
            ContentType=file_type,
            ServerSideEncryption='AES256',
            ACL='private'
        )
        
        logger.info(f"Termo salvo no S3 para prontuário: {prontuario}")
        return {"success": True, "message": "Termo de aceite enviado com sucesso", "prontuario": prontuario}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer upload do termo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar arquivo")

@app.post("/pacientes/", response_model=schemas.Paciente)
async def create_paciente(
    paciente: schemas.PacienteCreate = Body(...),
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
    if limit > 100:
        limit = 100
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
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
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
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
    return db_paciente

@app.delete("/pacientes/{paciente_id}")
def delete_paciente(
    paciente_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    deleted = crud.delete_paciente(db, paciente_id=paciente_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
    return {"success": True}

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
@app.post("/upload-mobile/{session_id}")
@limiter.limit("3/minute")  # Reduzido para 3 uploads por minuto por IP
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
        
        # Verificar limite de uploads por sessão
        with session_lock:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                if session['uploads_count'] >= session['max_uploads']:
                    logger.warning(f"Limite de uploads excedido para sessão: {session_id[:8]}...")
                    raise HTTPException(status_code=429, detail="Limite de uploads excedido para esta sessão")
                
                session['uploads_count'] += 1
        
        # Log seguro (sem dados sensíveis)
        logger.info(f"Upload recebido para sessão: {session_id[:8]}...")
        
        # Salvar temporário no S3 (para desktop recuperar)
        s3_service.save_upload(session_id, file_data.dict())
        
        # Salvar termo definitivo no S3
        header, data = file_data.fileData.split(',', 1)
        file_content = base64.b64decode(data)
        termo_key = f"termos/{file_data.prontuario}/termo_aceite.pdf"
        
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket,
            Key=termo_key,
            Body=file_content,
            ContentType=file_data.fileType,
            ServerSideEncryption='AES256',
            ACL='private'
        )
        
        logger.info(f"Termo salvo no S3 para prontuário: {file_data.prontuario}")
        
        return {"success": True, "message": "Arquivo recebido com sucesso", "prontuario": file_data.prontuario}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/upload-status/{session_id}")
@limiter.limit("30/minute")  # Reduzido para 30 verificações por minuto
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
@limiter.limit("5/minute")  # Reduzido para 5 sessões por minuto
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

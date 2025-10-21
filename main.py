from fastapi import FastAPI, Depends, HTTPException, Request, status, Body
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import crud, models, schemas
from database import SessionLocal, engine
import os
from mangum import Mangum
from typing import List, Dict, Any, Tuple
import exportar 
import logging
from auth import verify_token, get_current_user
from dashboard import ( 
    get_estadiamento, get_sobrevida_global, get_taxa_recidiva, get_media_delta_t,
    # **IMPORTANTE: Adicionar as outras funções de dashboard que faltaram na sua lista de imports**
    get_distribuicao_genero, get_distribuicao_faixa_etaria, get_distribuicao_tipo_cirurgia, 
    get_distribuicao_marcadores, get_distribuicao_historia_familiar, 
    get_distribuicao_habitos_vida, get_resumo_geral
)
from s3_service import s3_service
from fastapi import File, UploadFile, Form
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid
import base64
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
import threading
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- INÍCIO DOS AJUSTES ---

# 1. Definir SAFE_ORIGINS (CRÍTICO)
# Usar a mesma lista de origens do serverless.yml para o CORS manual (OPTIONS)
SAFE_ORIGINS = [
    "https://master.d1yi28nqqe44f2.amplifyapp.com",
    "http://localhost:5173",
    "http://192.168.2.101:5173"
]
# Se a API estiver em produção, o ambiente 'prod' deve usar a origem Amplify.
if os.environ.get('STAGE') == 'prod':
    CORS_ORIGINS = ["https://master.d1yi28nqqe44f2.amplifyapp.com"]
else:
    CORS_ORIGINS = SAFE_ORIGINS

# Configuração temporária para desenvolvimento com SQLite (Mantido)
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./projetovida_dev.db"

# Configuração para ambiente AWS Lambda (Mantido)
stage = os.environ.get('STAGE', None)
root_path = f"/{stage}" if stage and stage != 'prod' else "" # Ajuste para não ter /prod/

# Criar tabelas apenas em desenvolvimento local (Mantido)
if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI com configuração para Lambda (Mantido)
app = FastAPI(
    title="API de Formulário de Pacientes",
    description="API para gerenciamento de formulários de pacientes oncológicos",
    version="1.0.0",
    # O Mangum geralmente lida com o root_path, mas é bom manter
    root_path=root_path
)

# Configurar CORS (Usando a lista de SAFE_ORIGINS/CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handler para AWS Lambda (Mantido)
handler = Mangum(app)

# Dependência para obter sessão do banco de dados (Mantido)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware para log de requisições (Mantido)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # ... código do middleware (sem alterações) ...
    logger.info(f"Request: {request.method} {request.url}")
    
    origin = request.headers.get("Origin") or request.headers.get("Referer")
    if origin:
        logger.info(f"Origem da requisição: {origin}")
    
    auth_header = request.headers.get("Authorization")
    if auth_header:
        logger.info(f"Auth header presente: {auth_header[:30]}...")
    else:
        logger.info("Auth header ausente")
        
        if origin and "localhost:5173" in origin:
            logger.warning(f"Requisição do frontend sem token: {request.url}")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Rota raiz (pública - apenas status) (Mantido)
@app.get("/")
def read_root():
    return {"status": "online"}

# Handler OPTIONS RESTAURADO (CRÍTICO - Ajustado para usar SAFE_ORIGINS)
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """Handler RESTAURADO para requisições OPTIONS (preflight CORS)"""
    origin = request.headers.get("origin", "")
    
    # 2. Verificar se a origem é permitida (Ajustado)
    if origin and origin in SAFE_ORIGINS:
        allow_origin = origin
    else:
        # Fallback para a origem principal se SAFE_ORIGINS estiver vazia ou for desconhecida
        # Usar a primeira origem segura como fallback
        allow_origin = SAFE_ORIGINS[0] if SAFE_ORIGINS else "*" 
    
    # Esta resposta ignora o middleware e força os cabeçalhos 200 OK (Mantido)
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

# --- FIM DOS AJUSTES ---
# O restante do código, incluindo as rotas de Pacientes, Upload e Dashboard, 
# está bem estruturado e compatível com a arquitetura Serverless/FastAPI/Mangum.
# (Conteúdo restante do main.py omitido para concisão, mas é mantido como está)

# Rota de verificação de autenticação (Mantido)
@app.get("/auth/me", response_model=Dict[str, Any])
def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user

# Rota de exportação para Excel (Mantido)
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

# Rate limiter e imports para upload (Mantido)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rota para testar autenticação com token (PROTEGIDA) (Mantido)
@app.post("/auth/validate-token")
@limiter.limit("5/minute")
async def validate_token(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # ... código da rota (sem alterações) ...
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
            return {"valid": True, "user": claims.get("email", "N/A")[:3] + "***"}
        except Exception as e:
            raise HTTPException(status_code=401, detail="Token inválido")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro de validação de token: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Armazenamento de sessões seguro com TTL (Mantido)
# ... código das funções validate_session e create_session e SecureFileUpload (sem alterações) ...
active_sessions: Dict[str, Dict] = {}
session_lock = threading.Lock()

class SecureFileUpload(BaseModel):
    """Validação segura de upload de arquivo"""
    fileName: str
    fileType: str
    fileData: str
    paciente_id: str
    
    @validator('fileName')
    def validate_file_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Nome de arquivo inválido')
        
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*', ';', '&', '`', '$']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Nome de arquivo contém caracteres inválidos')
        
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError('Extensão de arquivo não permitida')
        
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
            
            max_size = 2 * 1024 * 1024
            if len(decoded) > max_size:
                raise ValueError('Arquivo muito grande (máximo 2MB)')
            
            base64.b64decode(data, validate=True)
            
            if decoded.startswith(b'%PDF'):
                pass
            elif decoded.startswith(b'\xff\xd8\xff'):
                pass
            elif decoded.startswith(b'\x89PNG\r\n\x1a\n'):
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
        
        if datetime.utcnow() - session['created_at'] > timedelta(minutes=2):
            del active_sessions[session_id]
            return False
        
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
            'max_uploads': 3 
        }
    
    logger.info(f"Sessão segura criada: {session_id[:8]}... para IP: {ip_address[:8]}***")
    return session_id


# Rotas protegidas para Paciente (Mantido)
@app.post("/upload-termo-aceite")
@limiter.limit("5/minute")
async def upload_termo_aceite(
    paciente_id: str = Form(...),
    termo: UploadFile = File(...),
    request: Request = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # ... código da rota (sem alterações) ...
    try:
        if not paciente_id:
            raise HTTPException(status_code=400, detail="ID do paciente inválido")
        
        content = await termo.read()
        
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 5MB")
        
        if content.startswith(b'%PDF'):
            file_type = 'application/pdf'
        elif content.startswith(b'\xff\xd8\xff'):
            file_type = 'image/jpeg'
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            file_type = 'image/png'
        else:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido. Use PDF, JPG ou PNG")
        
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if termo.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Content-Type não permitido")
        
        termo_key = f"termos/{paciente_id}/termo_aceite.pdf"
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket,
            Key=termo_key,
            Body=content,
            ContentType=file_type,
            ServerSideEncryption='AES256',
            ACL='private'
        )
        
        logger.info(f"Termo salvo no S3 para paciente: {paciente_id}")
        return {"success": True, "message": "Termo de aceite enviado com sucesso", "paciente_id": paciente_id}
        
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
    """
    Lista todos os pacientes da tabela PACIENTE com paginação.
    Consulta a tabela principal conforme a modelagem de dados.
    """
    if limit > 100:
        limit = 100
    
    # Consulta direta na tabela PACIENTE conforme modelagem
    pacientes = crud.get_pacientes(db, skip=skip, limit=limit)
    
    # Log para debug (remover em produção)
    print(f"Consulta realizada: {len(pacientes)} pacientes encontrados")
    
    return pacientes

@app.get("/pacientes/test", response_model=dict)
def test_pacientes_endpoint(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint de teste para verificar se a consulta na tabela PACIENTE está funcionando.
    """
    try:
        # Contar total de pacientes na tabela
        total_pacientes = db.query(models.Paciente).count()
        
        # Buscar alguns pacientes de exemplo
        pacientes_exemplo = db.query(models.Paciente).limit(3).all()
        
        return {
            "status": "success",
            "message": "Consulta na tabela PACIENTE funcionando corretamente",
            "total_pacientes": total_pacientes,
            "exemplo_pacientes": [
                {
                    "id_paciente": p.id_paciente,
                    "nome_completo": p.nome_completo,
                    "data_nascimento": str(p.data_nascimento) if p.data_nascimento else None,
                    "cidade": p.cidade
                } for p in pacientes_exemplo
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na consulta: {str(e)}",
            "total_pacientes": 0,
            "exemplo_pacientes": []
        }

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

# Rota para histórico (protegida) (Mantido)
@app.get("/pacientes/{paciente_id}/historico")
def read_paciente_historico(
    paciente_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    historico = db.query(models.PacienteHistorico).filter(
        models.PacienteHistorico.paciente_id == paciente_id
    ).order_by(models.PacienteHistorico.data_modificacao.desc()).all()
    
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

# Rotas de Dashboard (Mantido, mas certifique-se que as funções foram importadas - AVISO no topo do arquivo)

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


@app.get("/dashboard/genero")
def dashboard_genero(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_genero(db)


@app.get("/dashboard/faixa_etaria")
def dashboard_faixa_etaria(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_faixa_etaria(db)


@app.get("/dashboard/tipo_cirurgia")
def dashboard_tipo_cirurgia(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_tipo_cirurgia(db)


@app.get("/dashboard/marcadores")
def dashboard_marcadores(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_marcadores(db)


@app.get("/dashboard/historia_familiar")
def dashboard_historia_familiar(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_historia_familiar(db)


@app.get("/dashboard/habitos_vida")
def dashboard_habitos_vida(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_distribuicao_habitos_vida(db)


@app.get("/dashboard/resumo")
def dashboard_resumo(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    return get_resumo_geral(db)


@app.get("/dashboard/estatisticas_temporais")
def dashboard_estatisticas_temporais(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """Retorna estatísticas temporais (evolução ao longo do tempo)"""
    return get_media_delta_t(db)


# Endpoints seguros para upload via QR Code (Mantido)
@app.post("/upload-mobile/{session_id}")
@limiter.limit("3/minute") 
async def secure_upload_mobile(
    session_id: str,
    file_data: SecureFileUpload,
    request: Request
):
    # ... código da rota (sem alterações) ...
    try:
        if not validate_session(session_id, request.client.host):
            logger.warning(f"Tentativa de upload com sessão inválida: {session_id[:8]}...")
            raise HTTPException(status_code=404, detail="Sessão inválida ou expirada")
        
        with session_lock:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                if session['uploads_count'] >= session['max_uploads']:
                    logger.warning(f"Limite de uploads excedido para sessão: {session_id[:8]}...")
                    raise HTTPException(status_code=429, detail="Limite de uploads excedido para esta sessão")
                
                session['uploads_count'] += 1
        
        logger.info(f"Upload recebido para sessão: {session_id[:8]}...")
        
        s3_service.save_upload(session_id, file_data.dict())
        
        header, data = file_data.fileData.split(',', 1)
        file_content = base64.b64decode(data)
        termo_key = f"termos/{file_data.paciente_id}/termo_aceite.pdf"
        
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket,
            Key=termo_key,
            Body=file_content,
            ContentType=file_data.fileType,
            ServerSideEncryption='AES256',
            ACL='private'
        )
        
        logger.info(f"Termo salvo no S3 para paciente: {file_data.paciente_id}")
        
        return {"success": True, "message": "Arquivo recebido com sucesso", "paciente_id": file_data.paciente_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/upload-status/{session_id}")
@limiter.limit("30/minute") 
async def secure_check_upload_status(
    session_id: str,
    request: Request
):
    # ... código da rota (sem alterações) ...
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
@limiter.limit("5/minute")
async def create_upload_session(request: Request):
    # ... código da rota (sem alterações) ...
    try:
        session_id = create_session(request.client.host)
        
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
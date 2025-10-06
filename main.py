from fastapi import FastAPI, Depends, HTTPException, Request, status, Body
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
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

# Criar tabelas no banco de dados
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
    allow_origins=["http://localhost:5173"],  # Origem do frontend React/Vite
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

# Endpoints para upload via QR Code
@app.post("/upload-mobile/{session_id}")
async def upload_mobile(session_id: str, file_data: Dict[str, Any] = Body(...)):
    """Recebe arquivo do celular e armazena no S3"""
    try:
        s3_service.save_upload(session_id, {
            "fileName": file_data.get("fileName"),
            "fileType": file_data.get("fileType"),
            "base64Data": file_data.get("fileData")
        })
        return {"success": True, "message": "Arquivo recebido"}
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upload-status/{session_id}")
async def check_upload_status(session_id: str):
    """Verifica se arquivo foi enviado para esta sessão"""
    data = s3_service.get_upload(session_id)
    if data:
        return data
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")

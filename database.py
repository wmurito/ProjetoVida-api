from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json
import boto3
from botocore.exceptions import ClientError

# 🔥 Carregar variáveis do .env
load_dotenv()

def get_database_url():
    """Obtém URL do banco de dados do Secrets Manager ou .env"""
    # Se estiver no Lambda, buscar do Secrets Manager
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        secret_name = os.environ.get("DB_SECRET_NAME", "projeto-vida/database")
        try:
            client = boto3.client('secretsmanager')
            response = client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response['SecretString'])
            
            # Construir URL do PostgreSQL
            return f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}"
        except ClientError as e:
            raise Exception(f"Erro ao obter credenciais do banco: {str(e)}")
    
    # Desenvolvimento local: usar .env
    return os.getenv("DATABASE_URL", "sqlite:///./projetovida_dev.db")

# 🔗 Pegar a URL do banco
DATABASE_URL = get_database_url()

# 🔧 Criar engine com opções para AWS Lambda ou SQLite
if DATABASE_URL.startswith("sqlite"):
    # Configuração para SQLite (desenvolvimento)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Configuração para PostgreSQL (produção)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexão antes de usar
        pool_recycle=3600,   # Recicla conexões após 1 hora
        pool_size=5,         # Tamanho do pool de conexões
        max_overflow=10      # Máximo de conexões extras
    )

# 🏗️ Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base para os models
Base = declarative_base()
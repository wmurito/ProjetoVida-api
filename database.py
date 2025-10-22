from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json
import boto3
from botocore.exceptions import ClientError

# Carregar variáveis do .env
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
            # NOTA: O ajuste para o esquema 'clinical' será feito abaixo na função create_engine,
            # mas você também pode adicionar o parâmetro de options aqui:
            # return f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}?options=-csearch_path=clinical"
            return f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}"
        except ClientError as e:
            raise Exception(f"Erro ao obter credenciais do banco: {str(e)}")
    
    # Desenvolvimento local: usar .env ou construir URL PostgreSQL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Se não há DATABASE_URL, tentar construir a partir das variáveis individuais
    host = os.getenv("DB_HOST")
    if host:
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "projetovida")
        username = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "password")
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    # Fallback para SQLite se não houver configuração PostgreSQL
    return "sqlite:///./projetovida_dev.db"

#  Pegar a URL do banco
DATABASE_URL = get_database_url()

# Criar engine com opções para AWS Lambda ou SQLite
if DATABASE_URL.startswith("sqlite"):
    # Configuração para SQLite (desenvolvimento)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Configuração para PostgreSQL (produção)
    # A ÚNICA MUDANÇA É AQUI: search_path=clinical
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "sslmode": "prefer",
            "connect_timeout": 10,
            "options": "-c search_path=clinical"  # Ajuste do schema padrão
        }
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
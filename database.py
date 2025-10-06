from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 🔥 Carregar variáveis do .env
load_dotenv()

# 🔗 Pegar a URL do banco
DATABASE_URL = os.getenv("DATABASE_URL")

# 🚨 Verificar se a variável foi carregada
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada. Verifique seu arquivo .env")

# 🔧 Criar engine com opções para AWS Lambda
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
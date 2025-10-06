from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 🔧 Configuração para desenvolvimento com SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./projetovida_dev.db")

# 🏗️ Criar engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 🏗️ Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base para os models
Base = declarative_base()



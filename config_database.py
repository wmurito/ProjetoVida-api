"""
Configuração do banco de dados PostgreSQL para o Projeto Vida
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

def get_postgresql_url():
    """Constrói URL de conexão PostgreSQL"""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "projetovida")
    username = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def create_database_if_not_exists():
    """Cria o banco de dados se não existir"""
    # Conectar ao PostgreSQL sem especificar database
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    username = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    database = os.getenv("DB_NAME", "projetovida")
    
    # URL para conectar ao PostgreSQL (sem database específico)
    admin_url = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    
    try:
        admin_engine = create_engine(admin_url)
        with admin_engine.connect() as conn:
            # Verificar se o banco existe
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": database})
            
            if not result.fetchone():
                # Criar o banco
                conn.execute(text("COMMIT"))  # Sair da transação atual
                conn.execute(text(f"CREATE DATABASE {database}"))
                print(f"Banco de dados '{database}' criado com sucesso!")
            else:
                print(f"Banco de dados '{database}' já existe.")
                
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        raise

def get_engine():
    """Retorna engine configurado para PostgreSQL"""
    database_url = get_postgresql_url()
    
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "sslmode": "prefer",
            "connect_timeout": 10
        }
    )

def get_session_local():
    """Retorna SessionLocal configurado"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configurações para uso
if __name__ == "__main__":
    # Criar banco se não existir
    create_database_if_not_exists()
    
    # Testar conexão
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print("Conexão com PostgreSQL estabelecida com sucesso!")
            print(f"Versão: {result.fetchone()[0]}")
    except Exception as e:
        print(f"Erro na conexão: {e}")

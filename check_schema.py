"""Script para verificar e criar o schema public no PostgreSQL"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Conectar ao banco
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

# Verificar se o schema public existe
cursor.execute("""
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name = 'public';
""")

result = cursor.fetchone()

if result:
    print("[OK] Schema 'public' ja existe")
else:
    print("[AVISO] Schema 'public' nao existe. Criando...")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS public;")
    conn.commit()
    print("[OK] Schema 'public' criado com sucesso")

# Garantir que o usuário tem permissões no schema public
cursor.execute(f"""
    GRANT ALL ON SCHEMA public TO {os.getenv("DB_USER")};
    GRANT ALL ON ALL TABLES IN SCHEMA public TO {os.getenv("DB_USER")};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {os.getenv("DB_USER")};
""")
conn.commit()
print(f"[OK] Permissoes concedidas ao usuario {os.getenv('DB_USER')}")

cursor.close()
conn.close()

print("\n[OK] Verificacao concluida! Agora voce pode rodar: uvicorn main:app --reload")

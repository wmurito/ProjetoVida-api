"""
Migration: Remove NOT NULL constraints from optional clinical history columns.
Run this script ONCE against the production PostgreSQL database.
"""
from database import engine

SQL = """
-- Remover NOT NULL das colunas opcionais da tabela PACIENTE (schema clinical)
ALTER TABLE clinical.paciente ALTER COLUMN data_nascimento DROP NOT NULL;
ALTER TABLE clinical.paciente ALTER COLUMN hd_sinal_sintoma_principal DROP NOT NULL;
ALTER TABLE clinical.paciente ALTER COLUMN hd_data_sintomas DROP NOT NULL;
ALTER TABLE clinical.paciente ALTER COLUMN hd_idade_diagnostico DROP NOT NULL;
ALTER TABLE clinical.paciente ALTER COLUMN hd_lado_acometido DROP NOT NULL;
"""

if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(SQL)
        conn.execute("COMMIT")
    print("✅ Migration aplicada com sucesso!")
    print("   - data_nascimento: NOT NULL removido")
    print("   - hd_sinal_sintoma_principal: NOT NULL removido")
    print("   - hd_data_sintomas: NOT NULL removido")
    print("   - hd_idade_diagnostico: NOT NULL removido")
    print("   - hd_lado_acometido: NOT NULL removido")

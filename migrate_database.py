#!/usr/bin/env python3
"""
🔄 Script de Migração do Banco de Dados
Atualiza o banco de dados para incluir os novos modelos e campos
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, engine, SessionLocal
import models

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("🔄 Criando tabelas no banco de dados...")
    
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def check_tables():
    """Verifica se as tabelas foram criadas corretamente"""
    print("🔍 Verificando tabelas criadas...")
    
    try:
        db = SessionLocal()
        
        # Lista de tabelas esperadas
        expected_tables = [
            'paciente', 'historia_patologica', 'historia_familiar', 'familiar',
            'habitos_de_vida', 'paridade', 'historia_doenca_atual', 'modelos_preditores',
            'cirurgia_mama', 'cirurgia_axila', 'reconstrucao',
            'quimioterapia', 'radioterapia', 'endocrinoterapia', 'imunoterapia',
            'imunohistoquimica', 'core_biopsy', 'mamotomia', 'paaf',
            'desfecho', 'metastase', 'tempos_diagnostico', 'evento',
            'paciente_historico'
        ]
        
        # Verificar se as tabelas existem
        for table in expected_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM masto.{table}"))
                count = result.scalar()
                print(f"✅ Tabela {table}: {count} registros")
            except Exception as e:
                print(f"❌ Tabela {table}: Erro - {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def test_models():
    """Testa a criação de um registro em cada modelo"""
    print("🧪 Testando criação de registros...")
    
    try:
        db = SessionLocal()
        
        # Criar um paciente de teste
        paciente_teste = models.Paciente(
            nome_completo="Paciente Teste",
            cpf="12345678901",
            prontuario="TEST001",
            genero="feminino",
            data_nascimento="1990-01-01",
            telefone="11999999999",
            email="teste@teste.com"
        )
        
        db.add(paciente_teste)
        db.commit()
        db.refresh(paciente_teste)
        
        print(f"✅ Paciente criado: ID {paciente_teste.paciente_id}")
        
        # Testar criação de dados relacionados
        historia_patologica = models.HistoriaPatologica(
            paciente_id=paciente_teste.paciente_id,
            has=True,
            diabetes=False,
            hipertensao=True
        )
        db.add(historia_patologica)
        
        familiar = models.Familiar(
            paciente_id=paciente_teste.paciente_id,
            parentesco="mãe",
            tipo_cancer="mama",
            idade_diagnostico=45
        )
        db.add(familiar)
        
        cirurgia_mama = models.CirurgiaMama(
            paciente_id=paciente_teste.paciente_id,
            data="2023-01-01",
            tecnica="mastectomia",
            margens="livres"
        )
        db.add(cirurgia_mama)
        
        db.commit()
        print("✅ Dados relacionados criados com sucesso!")
        
        # Limpar dados de teste
        db.delete(paciente_teste)
        db.commit()
        print("✅ Dados de teste removidos")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelos: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando migração do banco de dados...")
    print("=" * 50)
    
    # Verificar configuração do banco
    database_url = os.getenv("DATABASE_URL", "sqlite:///./projetovida_dev.db")
    print(f"📊 Banco de dados: {database_url}")
    
    # Criar tabelas
    if not create_tables():
        print("❌ Falha na criação das tabelas")
        return False
    
    print()
    
    # Verificar tabelas
    if not check_tables():
        print("❌ Falha na verificação das tabelas")
        return False
    
    print()
    
    # Testar modelos
    if not test_models():
        print("❌ Falha no teste dos modelos")
        return False
    
    print()
    print("🎉 Migração concluída com sucesso!")
    print("✅ Banco de dados atualizado e funcional")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

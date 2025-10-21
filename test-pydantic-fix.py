#!/usr/bin/env python3
"""
Script para testar se as correções do Pydantic funcionam localmente
antes de fazer o deploy para o Lambda.
"""

import sys
import os

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("=== TESTANDO IMPORTS ===")
    
    try:
        print("Testando import do Pydantic...")
        from pydantic import BaseModel, validator
        print("✓ Pydantic importado com sucesso")
        
        print("Testando import do FastAPI...")
        from fastapi import FastAPI
        print("✓ FastAPI importado com sucesso")
        
        print("Testando import do Mangum...")
        from mangum import Mangum
        print("✓ Mangum importado com sucesso")
        
        print("Testando import dos schemas...")
        import schemas
        print("✓ Schemas importados com sucesso")
        
        print("Testando import do main...")
        import main
        print("✓ Main importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"✗ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False

def test_pydantic_models():
    """Testa se os modelos Pydantic funcionam corretamente"""
    print("\n=== TESTANDO MODELOS PYDANTIC ===")
    
    try:
        from pydantic import BaseModel, validator
        
        # Teste básico de modelo
        class TestModel(BaseModel):
            name: str
            age: int
            
            @validator('age')
            def validate_age(cls, v):
                if v < 0:
                    raise ValueError('Idade deve ser positiva')
                return v
        
        # Teste de criação
        test_data = {"name": "João", "age": 30}
        model = TestModel(**test_data)
        print(f"✓ Modelo criado com sucesso: {model}")
        
        # Teste de validação
        try:
            invalid_data = {"name": "João", "age": -5}
            TestModel(**invalid_data)
            print("✗ Validação falhou - deveria ter rejeitado idade negativa")
            return False
        except ValueError:
            print("✓ Validação funcionando corretamente")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nos modelos Pydantic: {e}")
        return False

def test_schemas():
    """Testa se os schemas do projeto funcionam"""
    print("\n=== TESTANDO SCHEMAS DO PROJETO ===")
    
    try:
        import schemas
        
        # Teste de criação de um schema básico
        familiar_data = {
            "nome": "Maria",
            "parentesco": "Mãe",
            "genero": "F",
            "tem_cancer_mama": True
        }
        
        familiar = schemas.FamiliarCreate(**familiar_data)
        print(f"✓ Schema Familiar criado: {familiar.nome}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nos schemas: {e}")
        return False

def main():
    """Função principal do teste"""
    print("CORREÇÃO DO ERRO PYDANTIC_CORE - TESTE LOCAL")
    print("=" * 50)
    
    # Verificar versão do Python
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print()
    
    # Executar testes
    tests = [
        test_imports,
        test_pydantic_models,
        test_schemas
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Resultado final
    print("=" * 50)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("✓ TODOS OS TESTES PASSARAM!")
        print("✓ As correções estão funcionando localmente")
        print("✓ Você pode prosseguir com o deploy para o Lambda")
        return 0
    else:
        print("✗ ALGUNS TESTES FALHARAM!")
        print("✗ Verifique as dependências antes de fazer o deploy")
        return 1

if __name__ == "__main__":
    sys.exit(main())

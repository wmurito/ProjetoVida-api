#!/usr/bin/env python3
"""
🧪 Teste de Segurança - Sistema de Upload via QR Code
Script para testar as correções de segurança implementadas
"""

import requests
import json
import time
import base64

# Configuração
BASE_URL = "http://localhost:8000"  # Ajustar conforme necessário

def test_secure_upload():
    """Testa o sistema de upload seguro"""
    print("🔒 Testando Sistema de Upload Seguro")
    print("=" * 50)
    
    # Teste 1: Criar sessão
    print("\n1. Testando criação de sessão...")
    try:
        response = requests.post(f"{BASE_URL}/create-upload-session")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"✅ Sessão criada: {session_id[:8]}...")
        else:
            print(f"❌ Falha ao criar sessão: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao criar sessão: {e}")
        return
    
    # Teste 2: Upload válido
    print("\n2. Testando upload válido...")
    valid_file_data = {
        "fileName": "test.pdf",
        "fileType": "application/pdf",
        "fileData": "data:application/pdf;base64,dGVzdA=="  # "test" em base64
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload-mobile/{session_id}",
            json=valid_file_data
        )
        if response.status_code == 200:
            print("✅ Upload válido aceito")
        else:
            print(f"❌ Upload válido rejeitado: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro no upload válido: {e}")
    
    # Teste 3: Upload com nome perigoso
    print("\n3. Testando upload com nome perigoso...")
    malicious_file_data = {
        "fileName": "../../../etc/passwd",
        "fileType": "application/pdf",
        "fileData": "data:application/pdf;base64,dGVzdA=="
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload-mobile/{session_id}",
            json=malicious_file_data
        )
        if response.status_code == 422:
            print("✅ Upload com nome perigoso bloqueado")
        else:
            print(f"❌ Upload com nome perigoso aceito: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de nome perigoso: {e}")
    
    # Teste 4: Upload com tipo inválido
    print("\n4. Testando upload com tipo inválido...")
    invalid_type_data = {
        "fileName": "test.exe",
        "fileType": "application/x-executable",
        "fileData": "data:application/x-executable;base64,dGVzdA=="
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload-mobile/{session_id}",
            json=invalid_type_data
        )
        if response.status_code == 422:
            print("✅ Upload com tipo inválido bloqueado")
        else:
            print(f"❌ Upload com tipo inválido aceito: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de tipo inválido: {e}")
    
    # Teste 5: Upload com arquivo muito grande
    print("\n5. Testando upload com arquivo muito grande...")
    large_file_data = {
        "fileName": "large.pdf",
        "fileType": "application/pdf",
        "fileData": "data:application/pdf;base64," + "A" * 10000000  # 10MB
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload-mobile/{session_id}",
            json=large_file_data
        )
        if response.status_code == 422:
            print("✅ Upload com arquivo grande bloqueado")
        else:
            print(f"❌ Upload com arquivo grande aceito: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de arquivo grande: {e}")
    
    # Teste 6: Rate limiting
    print("\n6. Testando rate limiting...")
    rate_limit_count = 0
    for i in range(10):  # Tentar 10 uploads rapidamente
        try:
            response = requests.post(
                f"{BASE_URL}/upload-mobile/{session_id}",
                json=valid_file_data
            )
            if response.status_code == 429:
                rate_limit_count += 1
        except Exception as e:
            print(f"Erro no teste de rate limiting: {e}")
    
    if rate_limit_count > 0:
        print(f"✅ Rate limiting funcionando ({rate_limit_count} bloqueios)")
    else:
        print("⚠️ Rate limiting não detectado")
    
    # Teste 7: Sessão inválida
    print("\n7. Testando sessão inválida...")
    try:
        response = requests.post(
            f"{BASE_URL}/upload-mobile/invalid-session",
            json=valid_file_data
        )
        if response.status_code == 404:
            print("✅ Sessão inválida bloqueada")
        else:
            print(f"❌ Sessão inválida aceita: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de sessão inválida: {e}")
    
    # Teste 8: Verificar status
    print("\n8. Testando verificação de status...")
    try:
        response = requests.get(f"{BASE_URL}/upload-status/{session_id}")
        if response.status_code in [200, 404]:
            print("✅ Verificação de status funcionando")
        else:
            print(f"❌ Erro na verificação de status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na verificação de status: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testes de segurança concluídos!")

def test_session_expiration():
    """Testa expiração de sessão"""
    print("\n⏰ Testando expiração de sessão...")
    
    # Criar sessão
    response = requests.post(f"{BASE_URL}/create-upload-session")
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"Sessão criada: {session_id[:8]}...")
        
        # Aguardar expiração (6 minutos)
        print("Aguardando expiração da sessão (6 minutos)...")
        print("⚠️ Este teste demora 6 minutos. Pressione Ctrl+C para cancelar.")
        
        try:
            time.sleep(360)  # 6 minutos
        except KeyboardInterrupt:
            print("\nTeste de expiração cancelado pelo usuário")
            return
        
        # Tentar usar sessão expirada
        valid_file_data = {
            "fileName": "test.pdf",
            "fileType": "application/pdf",
            "fileData": "data:application/pdf;base64,dGVzdA=="
        }
        
        response = requests.post(
            f"{BASE_URL}/upload-mobile/{session_id}",
            json=valid_file_data
        )
        
        if response.status_code == 404:
            print("✅ Sessão expirada corretamente bloqueada")
        else:
            print(f"❌ Sessão expirada ainda válida: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Iniciando Testes de Segurança do Upload")
    print("Certifique-se de que o servidor está rodando em", BASE_URL)
    print()
    
    # Testes básicos
    test_secure_upload()
    
    # Perguntar se quer testar expiração
    try:
        test_expiration = input("\nDeseja testar expiração de sessão? (s/N): ").lower()
        if test_expiration == 's':
            test_session_expiration()
    except KeyboardInterrupt:
        print("\nTestes cancelados pelo usuário")
    
    print("\n✅ Todos os testes concluídos!")




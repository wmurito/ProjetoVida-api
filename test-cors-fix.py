#!/usr/bin/env python3
"""
Script para testar se o CORS está funcionando corretamente
"""
import requests
import json

def test_cors():
    """Testa se o CORS está configurado corretamente"""
    
    # URLs para testar
    api_url = "https://80alai4x6c.execute-api.us-east-1.amazonaws.com"
    origin = "https://master.d1yi28nqqe44f2.amplifyapp.com"
    
    print("🧪 Testando CORS...")
    print(f"API URL: {api_url}")
    print(f"Origin: {origin}")
    print("-" * 50)
    
    # Teste 1: OPTIONS request (preflight)
    print("1. Testando requisição OPTIONS (preflight)...")
    try:
        response = requests.options(
            f"{api_url}/dashboard/estadiamento",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers CORS:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"     {header}: {value}")
        
        if response.status_code == 200:
            print("   ✅ Preflight CORS funcionando!")
        else:
            print("   ❌ Preflight CORS com problema")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 2: GET request
    print("2. Testando requisição GET...")
    try:
        response = requests.get(
            f"{api_url}/dashboard/estadiamento",
            headers={
                "Origin": origin,
                "Authorization": "Bearer test-token"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers CORS:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"     {header}: {value}")
        
        if "access-control-allow-origin" in response.headers:
            print("   ✅ CORS headers presentes!")
        else:
            print("   ❌ CORS headers ausentes")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 3: Verificar se API está online
    print("3. Verificando se API está online...")
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API online!")
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print("   ❌ API com problema")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    print("🎯 Resumo:")
    print("   Se todos os testes passaram, o CORS está funcionando!")
    print("   Se houver erros, verifique a configuração no serverless.yml")

if __name__ == "__main__":
    test_cors()

#!/usr/bin/env python3
"""
Teste final para verificar se o CORS está funcionando corretamente
após as correções implementadas.
"""
import requests
import json
from datetime import datetime

def test_cors_final():
    """Teste completo de CORS após correções"""
    
    print("🧪 TESTE FINAL DE CORS")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs para testar
    api_url = "https://80alai4x6c.execute-api.us-east-1.amazonaws.com"
    origin = "https://master.d1yi28nqqe44f2.amplifyapp.com"
    
    print(f"🌐 API URL: {api_url}")
    print(f"🎯 Origin: {origin}")
    print()
    
    # Teste 1: Verificar se API está online
    print("1️⃣ TESTE: API Online")
    print("-" * 30)
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
    
    # Teste 2: OPTIONS request (preflight) - TESTE PRINCIPAL
    print("2️⃣ TESTE: OPTIONS Request (Preflight)")
    print("-" * 30)
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
        
        # Verificar headers CORS
        cors_headers = {}
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                cors_headers[header] = value
        
        if cors_headers:
            print("   ✅ Headers CORS encontrados:")
            for header, value in cors_headers.items():
                print(f"     {header}: {value}")
                
            # Verificar se o header principal está presente
            if "access-control-allow-origin" in cors_headers:
                if cors_headers["access-control-allow-origin"] == origin:
                    print("   ✅ Access-Control-Allow-Origin correto!")
                else:
                    print(f"   ⚠️ Access-Control-Allow-Origin diferente: {cors_headers['access-control-allow-origin']}")
            else:
                print("   ❌ Access-Control-Allow-Origin ausente!")
        else:
            print("   ❌ Nenhum header CORS encontrado!")
        
        if response.status_code == 200:
            print("   ✅ Preflight CORS funcionando!")
        else:
            print("   ❌ Preflight CORS com problema")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 3: GET request com Origin
    print("3️⃣ TESTE: GET Request com Origin")
    print("-" * 30)
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
        
        # Verificar headers CORS na resposta
        cors_headers = {}
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                cors_headers[header] = value
        
        if cors_headers:
            print("   ✅ Headers CORS na resposta:")
            for header, value in cors_headers.items():
                print(f"     {header}: {value}")
        else:
            print("   ⚠️ Nenhum header CORS na resposta")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 4: Testar diferentes endpoints
    print("4️⃣ TESTE: Diferentes Endpoints")
    print("-" * 30)
    
    endpoints = [
        "/dashboard/estadiamento",
        "/dashboard/sobrevida", 
        "/dashboard/recidiva",
        "/dashboard/delta_t",
        "/pacientes/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.options(
                f"{api_url}{endpoint}",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "authorization,content-type"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: OK")
            else:
                print(f"   ❌ {endpoint}: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Erro - {e}")
    
    print()
    
    # Resumo final
    print("🎯 RESUMO FINAL")
    print("=" * 50)
    print("✅ Correções implementadas:")
    print("   - Handler OPTIONS removido do main.py")
    print("   - CORS configurado no serverless.yml")
    print("   - API Gateway HTTP API gerencia CORS automaticamente")
    print()
    print("📋 Próximos passos:")
    print("   1. Se todos os testes passaram, o CORS está funcionando!")
    print("   2. Recarregue sua aplicação no Amplify")
    print("   3. Teste as funcionalidades do dashboard")
    print("   4. Verifique se os erros de CORS desapareceram")
    print()
    print("🔗 URL da API: https://80alai4x6c.execute-api.us-east-1.amazonaws.com")
    print("🌐 Frontend: https://master.d1yi28nqqe44f2.amplifyapp.com")

if __name__ == "__main__":
    test_cors_final()

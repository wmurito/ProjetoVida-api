#!/usr/bin/env python3
import requests

# Teste simples de CORS
url = "https://pteq15e8a6.execute-api.us-east-1.amazonaws.com/"
headers = {
    "Origin": "https://master.d1yi28nqqe44f2.amplifyapp.com"
}

print("Testando CORS...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print("Headers CORS:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"  {key}: {value}")
except Exception as e:
    print(f"Erro: {e}")
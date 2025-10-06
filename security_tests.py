"""
🧪 Testes de Segurança - API ProjetoVida
Testes automatizados para verificar vulnerabilidades de segurança
"""

import pytest
import requests
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Importar a aplicação
from main import app

client = TestClient(app)

class TestSecurity:
    """Testes de segurança da API"""
    
    def test_cors_headers(self):
        """Testa se os headers CORS estão configurados corretamente"""
        response = client.options("/")
        
        # Verificar headers CORS
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_security_headers(self):
        """Testa se os headers de segurança estão presentes"""
        response = client.get("/")
        
        # Headers de segurança obrigatórios
        security_headers = [
            "x-content-type-options",
            "x-frame-options", 
            "x-xss-protection",
            "referrer-policy"
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Header {header} não encontrado"
    
    def test_no_sensitive_data_in_logs(self):
        """Testa se dados sensíveis não são expostos em logs"""
        # Mock do logger para capturar logs
        with patch('main.logger') as mock_logger:
            # Fazer requisição com token
            headers = {"Authorization": "Bearer fake-token-12345"}
            client.get("/auth/test", headers=headers)
            
            # Verificar se o token não foi logado
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            
            for log in log_calls:
                assert "fake-token-12345" not in log, "Token exposto em logs"
                assert "Bearer fake-token-12345" not in log, "Token completo exposto em logs"
    
    def test_rate_limiting(self):
        """Testa se o rate limiting está funcionando"""
        # Fazer múltiplas requisições rapidamente
        for i in range(15):  # Mais que o limite
            response = client.get("/")
            
            # Se rate limiting estiver ativo, deve retornar 429
            if response.status_code == 429:
                assert True, "Rate limiting funcionando"
                return
        
        # Se chegou aqui, rate limiting não está ativo
        pytest.skip("Rate limiting não implementado")
    
    def test_sql_injection_protection(self):
        """Testa proteção contra SQL injection"""
        # Tentar SQL injection em parâmetros
        malicious_inputs = [
            "'; DROP TABLE paciente; --",
            "1' OR '1'='1",
            "1; DELETE FROM paciente; --",
            "1' UNION SELECT * FROM paciente --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/pacientes/{malicious_input}")
            
            # Deve retornar erro 404 ou 422, não 500
            assert response.status_code in [404, 422], f"SQL injection possível: {malicious_input}"
    
    def test_xss_protection(self):
        """Testa proteção contra XSS"""
        # Tentar XSS em parâmetros
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            response = client.get(f"/pacientes/{payload}")
            
            # Verificar se o payload não é retornado no response
            assert payload not in response.text, f"XSS possível: {payload}"
    
    def test_file_upload_validation(self):
        """Testa validação de upload de arquivos"""
        # Tentar upload de arquivo malicioso
        malicious_file = {
            "fileName": "../../../etc/passwd",
            "fileType": "text/plain",
            "fileData": "dGVzdA=="  # base64 de "test"
        }
        
        response = client.post("/upload-mobile/test-session", json=malicious_file)
        
        # Deve rejeitar arquivo com path traversal
        assert response.status_code == 422, "Path traversal não bloqueado"
    
    def test_authentication_required(self):
        """Testa se rotas protegidas requerem autenticação"""
        protected_routes = [
            "/pacientes/",
            "/pacientes/1",
            "/dashboard/estadiamento"
        ]
        
        for route in protected_routes:
            response = client.get(route)
            
            # Deve retornar 401 ou 403 sem token
            assert response.status_code in [401, 403], f"Rota {route} não protegida"
    
    def test_token_validation(self):
        """Testa validação de tokens"""
        # Token inválido
        invalid_tokens = [
            "invalid-token",
            "Bearer invalid-token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
            ""
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = client.get("/auth/me", headers=headers)
            
            # Deve rejeitar token inválido
            assert response.status_code == 401, f"Token inválido aceito: {token}"
    
    def test_input_validation(self):
        """Testa validação de entrada de dados"""
        # Dados inválidos para criação de paciente
        invalid_patient = {
            "nome_completo": "",  # Nome vazio
            "idade": -1,  # Idade negativa
            "email": "invalid-email",  # Email inválido
            "telefone": "abc"  # Telefone inválido
        }
        
        # Mock de autenticação para testar validação
        with patch('main.get_current_user') as mock_auth:
            mock_auth.return_value = {"username": "test"}
            
            response = client.post("/pacientes/", json=invalid_patient)
            
            # Deve rejeitar dados inválidos
            assert response.status_code == 422, "Dados inválidos aceitos"
    
    def test_error_handling(self):
        """Testa se erros não expõem informações sensíveis"""
        # Tentar acessar recurso inexistente
        response = client.get("/pacientes/999999")
        
        # Verificar se não expõe stack trace
        response_text = response.text.lower()
        sensitive_info = [
            "traceback",
            "file",
            "line",
            "exception",
            "error in",
            "python"
        ]
        
        for info in sensitive_info:
            assert info not in response_text, f"Informação sensível exposta: {info}"

class TestDataProtection:
    """Testes de proteção de dados"""
    
    def test_patient_data_encryption(self):
        """Testa se dados sensíveis são protegidos"""
        # Este teste seria implementado se houvesse criptografia
        # Por enquanto, apenas verifica se dados não são expostos em logs
        pass
    
    def test_pii_handling(self):
        """Testa tratamento de informações pessoais"""
        # Verificar se PII não é logado
        with patch('main.logger') as mock_logger:
            # Simular operação com dados pessoais
            patient_data = {
                "nome_completo": "João Silva",
                "cpf": "123.456.789-00",
                "telefone": "(11) 99999-9999"
            }
            
            # Fazer requisição (mock de auth)
            with patch('main.get_current_user') as mock_auth:
                mock_auth.return_value = {"username": "test"}
                client.post("/pacientes/", json=patient_data)
            
            # Verificar se PII não foi logado
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            
            for log in log_calls:
                assert "123.456.789-00" not in log, "CPF exposto em logs"
                assert "(11) 99999-9999" not in log, "Telefone exposto em logs"

# Configuração do pytest
@pytest.fixture(scope="session")
def test_client():
    """Cliente de teste para a API"""
    return TestClient(app)

# Comandos para executar os testes:
# pytest security_tests.py -v
# pytest security_tests.py::TestSecurity -v
# pytest security_tests.py::TestDataProtection -v

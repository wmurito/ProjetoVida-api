#!/usr/bin/env python3
"""
🔒 Verificação de Segurança - ProjetoVida API
Script para verificar vulnerabilidades de segurança no código
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

class SecurityChecker:
    """Verificador de segurança para o código"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.info = []
    
    def check_hardcoded_secrets(self, file_path: str) -> List[Dict]:
        """Verifica secrets hardcoded no código"""
        issues = []
        
        # Padrões de secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Senha hardcoded"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Secret hardcoded"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API key hardcoded"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Token hardcoded"),
            (r'private_key\s*=\s*["\'][^"\']+["\']', "Chave privada hardcoded"),
            (r'aws_access_key\s*=\s*["\'][^"\']+["\']', "AWS access key hardcoded"),
            (r'aws_secret\s*=\s*["\'][^"\']+["\']', "AWS secret hardcoded"),
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'type': 'SECRET',
                                'description': description,
                                'content': line.strip()
                            })
        except Exception as e:
            print(f"Erro ao ler arquivo {file_path}: {e}")
        
        return issues
    
    def check_sql_injection(self, file_path: str) -> List[Dict]:
        """Verifica possíveis vulnerabilidades de SQL injection"""
        issues = []
        
        # Padrões perigosos
        dangerous_patterns = [
            (r'execute\s*\(\s*["\'].*%s.*["\']', "SQL injection - string formatting"),
            (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "SQL injection - f-string"),
            (r'execute\s*\(\s*["\'].*\+.*["\']', "SQL injection - concatenação"),
            (r'query\s*\(\s*["\'].*%s.*["\']', "SQL injection - query com %s"),
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'type': 'SQL_INJECTION',
                                'description': description,
                                'content': line.strip()
                            })
        except Exception as e:
            print(f"Erro ao ler arquivo {file_path}: {e}")
        
        return issues
    
    def check_logging_issues(self, file_path: str) -> List[Dict]:
        """Verifica problemas de logging"""
        issues = []
        
        # Padrões problemáticos
        logging_patterns = [
            (r'logger\.(info|debug|warning|error)\s*\(\s*f["\'].*\{.*\}.*["\']', "Logging com f-string pode expor dados"),
            (r'print\s*\(\s*.*token.*\)', "Print de token"),
            (r'print\s*\(\s*.*password.*\)', "Print de senha"),
            (r'logger\.(info|debug|warning|error)\s*\(\s*.*token.*\)', "Logging de token"),
            (r'logger\.(info|debug|warning|error)\s*\(\s*.*password.*\)', "Logging de senha"),
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in logging_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'type': 'LOGGING',
                                'description': description,
                                'content': line.strip()
                            })
        except Exception as e:
            print(f"Erro ao ler arquivo {file_path}: {e}")
        
        return issues
    
    def check_cors_config(self, file_path: str) -> List[Dict]:
        """Verifica configuração de CORS"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar CORS muito permissivo
                if 'allow_origins=["*"]' in content:
                    issues.append({
                        'file': file_path,
                        'line': 0,
                        'type': 'CORS',
                        'description': 'CORS muito permissivo - allow_origins=["*"]',
                        'content': 'allow_origins=["*"]'
                    })
                
                if 'allow_methods=["*"]' in content:
                    issues.append({
                        'file': file_path,
                        'line': 0,
                        'type': 'CORS',
                        'description': 'CORS muito permissivo - allow_methods=["*"]',
                        'content': 'allow_methods=["*"]'
                    })
                
                if 'allow_headers=["*"]' in content:
                    issues.append({
                        'file': file_path,
                        'line': 0,
                        'type': 'CORS',
                        'description': 'CORS muito permissivo - allow_headers=["*"]',
                        'content': 'allow_headers=["*"]'
                    })
        except Exception as e:
            print(f"Erro ao ler arquivo {file_path}: {e}")
        
        return issues
    
    def check_file_permissions(self, file_path: str) -> List[Dict]:
        """Verifica permissões de arquivo"""
        issues = []
        
        try:
            stat = os.stat(file_path)
            mode = stat.st_mode
            
            # Verificar se arquivo é muito permissivo
            if mode & 0o002:  # World writable
                issues.append({
                    'file': file_path,
                    'line': 0,
                    'type': 'PERMISSIONS',
                    'description': 'Arquivo com permissão de escrita para todos',
                    'content': f'Permissões: {oct(mode)}'
                })
        except Exception as e:
            print(f"Erro ao verificar permissões de {file_path}: {e}")
        
        return issues
    
    def scan_file(self, file_path: str):
        """Escaneia um arquivo em busca de vulnerabilidades"""
        if not file_path.endswith('.py'):
            return
        
        print(f"🔍 Escaneando: {file_path}")
        
        # Verificar diferentes tipos de vulnerabilidades
        self.vulnerabilities.extend(self.check_hardcoded_secrets(file_path))
        self.vulnerabilities.extend(self.check_sql_injection(file_path))
        self.vulnerabilities.extend(self.check_logging_issues(file_path))
        self.vulnerabilities.extend(self.check_cors_config(file_path))
        self.vulnerabilities.extend(self.check_file_permissions(file_path))
    
    def scan_directory(self, directory: str):
        """Escaneia um diretório recursivamente"""
        for root, dirs, files in os.walk(directory):
            # Pular diretórios desnecessários
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.scan_file(file_path)
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de segurança"""
        report = {
            'summary': {
                'total_vulnerabilities': len(self.vulnerabilities),
                'critical': len([v for v in self.vulnerabilities if v['type'] == 'SECRET']),
                'high': len([v for v in self.vulnerabilities if v['type'] == 'SQL_INJECTION']),
                'medium': len([v for v in self.vulnerabilities if v['type'] == 'LOGGING']),
                'low': len([v for v in self.vulnerabilities if v['type'] in ['CORS', 'PERMISSIONS']])
            },
            'vulnerabilities': self.vulnerabilities
        }
        
        return report
    
    def print_report(self):
        """Imprime relatório de segurança"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("🔒 RELATÓRIO DE SEGURANÇA - ProjetoVida API")
        print("="*60)
        
        print(f"\n📊 RESUMO:")
        print(f"   Total de vulnerabilidades: {report['summary']['total_vulnerabilities']}")
        print(f"   🔴 Críticas: {report['summary']['critical']}")
        print(f"   🟠 Altas: {report['summary']['high']}")
        print(f"   🟡 Médias: {report['summary']['medium']}")
        print(f"   🟢 Baixas: {report['summary']['low']}")
        
        if self.vulnerabilities:
            print(f"\n🚨 VULNERABILIDADES ENCONTRADAS:")
            print("-" * 60)
            
            for vuln in self.vulnerabilities:
                severity = "🔴" if vuln['type'] == 'SECRET' else \
                          "🟠" if vuln['type'] == 'SQL_INJECTION' else \
                          "🟡" if vuln['type'] == 'LOGGING' else "🟢"
                
                print(f"{severity} {vuln['type']}: {vuln['description']}")
                print(f"   📁 Arquivo: {vuln['file']}")
                if vuln['line'] > 0:
                    print(f"   📍 Linha: {vuln['line']}")
                print(f"   📝 Código: {vuln['content']}")
                print()
        else:
            print("\n✅ Nenhuma vulnerabilidade encontrada!")
        
        print("="*60)

def main():
    """Função principal"""
    checker = SecurityChecker()
    
    # Escanear diretório atual
    current_dir = os.getcwd()
    print(f"🔍 Iniciando verificação de segurança em: {current_dir}")
    
    checker.scan_directory(current_dir)
    checker.print_report()
    
    # Retornar código de saída baseado no número de vulnerabilidades
    if checker.vulnerabilities:
        critical_count = len([v for v in checker.vulnerabilities if v['type'] == 'SECRET'])
        if critical_count > 0:
            print(f"\n❌ Encontradas {critical_count} vulnerabilidades críticas!")
            sys.exit(1)
        else:
            print(f"\n⚠️  Encontradas {len(checker.vulnerabilities)} vulnerabilidades não críticas.")
            sys.exit(0)
    else:
        print("\n✅ Verificação de segurança concluída sem problemas!")
        sys.exit(0)

if __name__ == "__main__":
    main()

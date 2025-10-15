#!/usr/bin/env python3

"""
Script de Limpeza de Segurança - ProjetoVida API
Remove credenciais e dados sensíveis do repositório Git
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("🔒 Iniciando limpeza de segurança do repositório API...\n")

def check_git_repo():
    """Verifica se estamos em um repositório Git"""
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro: Não estamos em um repositório Git")
        return False

def file_exists(file_path):
    """Verifica se arquivo existe"""
    return os.path.exists(file_path)

def remove_from_git(file_path):
    """Remove arquivo do Git (mas mantém localmente)"""
    try:
        if file_exists(file_path):
            subprocess.run(['git', 'rm', '--cached', file_path], 
                          capture_output=True, check=True)
            print(f"✅ Removido do Git: {file_path}")
            return True
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao remover {file_path}: {e}")
        return False

def check_gitignore(file_path):
    """Verifica se arquivo está no .gitignore"""
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
            return file_path in content
    except FileNotFoundError:
        return False

def add_to_gitignore(file_path):
    """Adiciona arquivo ao .gitignore se não estiver"""
    try:
        gitignore_content = ""
        if file_exists('.gitignore'):
            with open('.gitignore', 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
        
        if file_path not in gitignore_content:
            gitignore_content += f"\n# Arquivo sensível removido automaticamente\n{file_path}\n"
            with open('.gitignore', 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print(f"✅ Adicionado ao .gitignore: {file_path}")
        else:
            print(f"ℹ️  Já está no .gitignore: {file_path}")
    except Exception as e:
        print(f"❌ Erro ao adicionar ao .gitignore: {e}")

def check_git_status():
    """Verifica status do Git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao verificar status do Git: {e}")
        return []

def check_secrets_in_files():
    """Verifica se há secrets hardcoded nos arquivos"""
    print("\n🔍 Verificando secrets hardcoded nos arquivos...")
    
    # Padrões de secrets para procurar
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'key\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'aws_access_key_id\s*=\s*["\'][^"\']+["\']',
        r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']'
    ]
    
    import re
    suspicious_files = []
    
    # Procurar em arquivos Python
    for py_file in Path('.').rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    suspicious_files.append((str(py_file), pattern))
                    break
        except Exception:
            continue
    
    if suspicious_files:
        print("🚨 Arquivos com possíveis secrets hardcoded:")
        for file_path, pattern in suspicious_files:
            print(f"   - {file_path} (padrão: {pattern})")
        print("\n⚠️  Recomendação: Mover secrets para variáveis de ambiente")
    else:
        print("✅ Nenhum secret hardcoded encontrado")

def main():
    print_header()
    
    print("🔍 Verificando repositório Git...")
    if not check_git_repo():
        sys.exit(1)
    
    print("✅ Repositório Git encontrado\n")
    
    # Arquivos sensíveis que devem ser removidos do Git
    sensitive_files = [
        '.env',
        '.env.local',
        '.env.production',
        '.env.staging',
        'config.local.py',
        'settings.local.py',
        'secrets.json',
        'credentials.json',
        'aws-credentials.json'
    ]
    
    print("🔍 Verificando arquivos sensíveis...")
    removed_count = 0
    
    for file_path in sensitive_files:
        print(f"\n📁 Verificando: {file_path}")
        
        if file_exists(file_path):
            print(f"⚠️  Arquivo sensível encontrado: {file_path}")
            
            # Verificar se está sendo rastreado pelo Git
            try:
                result = subprocess.run(['git', 'ls-files', file_path], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    print(f"🚨 Arquivo está sendo rastreado pelo Git!")
                    
                    if remove_from_git(file_path):
                        removed_count += 1
                        add_to_gitignore(file_path)
                else:
                    print(f"✅ Arquivo não está sendo rastreado pelo Git")
            except subprocess.CalledProcessError:
                print(f"✅ Arquivo não está sendo rastreado pelo Git")
        else:
            print(f"✅ Arquivo não encontrado")
    
    # Verificar secrets hardcoded
    check_secrets_in_files()
    
    print(f"\n📊 Resumo da limpeza:")
    print(f"   - Arquivos removidos do Git: {removed_count}")
    print(f"   - Arquivos verificados: {len(sensitive_files)}")
    
    if removed_count > 0:
        print(f"\n🚨 ATENÇÃO: {removed_count} arquivo(s) sensível(is) foi(ram) removido(s) do Git!")
        print(f"\n📋 Próximos passos:")
        print(f"   1. Commit as mudanças:")
        print(f"      git add .gitignore")
        print(f"      git commit -m \"security: Remove sensitive files from repository\"")
        print(f"   2. Push as mudanças:")
        print(f"      git push")
        print(f"   3. Configure as variáveis de ambiente no seu ambiente de produção")
        print(f"   4. Considere rotacionar as credenciais expostas")
    else:
        print(f"\n✅ Nenhum arquivo sensível encontrado no Git!")
    
    print(f"\n🔍 Verificando status atual do Git...")
    git_status = check_git_status()
    if git_status:
        print(f"\n📋 Mudanças pendentes:")
        for change in git_status:
            print(f"   {change}")
    else:
        print(f"\n✅ Nenhuma mudança pendente")
    
    print(f"\n🔒 Limpeza de segurança concluída!")

if __name__ == "__main__":
    main()

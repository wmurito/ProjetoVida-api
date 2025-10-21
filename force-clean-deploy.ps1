# Script para forçar uma limpeza completa e deploy
# Este script resolve o problema de cache persistente do Lambda

Write-Host "=== FORÇANDO LIMPEZA COMPLETA E DEPLOY ===" -ForegroundColor Red
Write-Host "Este script irá fazer uma limpeza agressiva para resolver o cache persistente" -ForegroundColor Yellow
Write-Host ""

# Parar qualquer processo em execução
Write-Host "Parando processos relacionados..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*serverless*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Limpeza agressiva de todos os caches e arquivos temporários
Write-Host "=== LIMPEZA AGRESSIVA DE CACHE ===" -ForegroundColor Red

# Remover .serverless
if (Test-Path ".serverless") {
    Remove-Item -Recurse -Force ".serverless"
    Write-Host "✓ .serverless removido" -ForegroundColor Green
}

# Remover node_modules
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "✓ node_modules removido" -ForegroundColor Green
}

# Remover package-lock.json
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
    Write-Host "✓ package-lock.json removido" -ForegroundColor Green
}

# Remover arquivos Python compilados
Write-Host "Removendo arquivos Python compilados..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object { 
    Remove-Item $_ -Force -ErrorAction SilentlyContinue 
}
Get-ChildItem -Path . -Recurse -Name "__pycache__" | ForEach-Object { 
    Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue 
}
Write-Host "✓ Arquivos Python compilados removidos" -ForegroundColor Green

# Limpar cache do npm global
Write-Host "Limpando cache do npm..." -ForegroundColor Yellow
npm cache clean --force 2>$null
Write-Host "✓ Cache do npm limpo" -ForegroundColor Green

# Verificar se o serverless está instalado
Write-Host "=== VERIFICANDO SERVERLESS FRAMEWORK ===" -ForegroundColor Yellow
try {
    $serverlessVersion = serverless --version 2>$null
    Write-Host "✓ Serverless Framework: $serverlessVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Serverless não encontrado. Instalando..." -ForegroundColor Red
    npm install -g serverless
    npm install -g serverless-python-requirements
    Write-Host "✓ Serverless instalado" -ForegroundColor Green
}

# Verificar se o Docker está rodando (necessário para dockerizePip)
Write-Host "=== VERIFICANDO DOCKER ===" -ForegroundColor Yellow
try {
    docker --version 2>$null | Out-Null
    Write-Host "✓ Docker está disponível" -ForegroundColor Green
} catch {
    Write-Host "⚠ Docker não encontrado. Isso pode causar problemas com dockerizePip" -ForegroundColor Yellow
    Write-Host "  Recomendado: Instalar Docker Desktop" -ForegroundColor Gray
}

# Verificar arquivos de dependências
Write-Host "=== VERIFICANDO DEPENDÊNCIAS ===" -ForegroundColor Yellow
if (Test-Path "requirements-lambda.txt") {
    Write-Host "✓ requirements-lambda.txt encontrado" -ForegroundColor Green
    $pydanticLine = Get-Content "requirements-lambda.txt" | Where-Object { $_ -like "*pydantic*" }
    Write-Host "  Pydantic configurado: $pydanticLine" -ForegroundColor Cyan
} else {
    Write-Host "✗ requirements-lambda.txt não encontrado!" -ForegroundColor Red
    exit 1
}

# Forçar remoção da função Lambda existente
Write-Host "=== REMOVENDO FUNÇÃO LAMBDA EXISTENTE ===" -ForegroundColor Red
Write-Host "Isso irá remover completamente a função atual..." -ForegroundColor Yellow
try {
    serverless remove --stage prod --verbose 2>$null
    Write-Host "✓ Função Lambda removida" -ForegroundColor Green
} catch {
    Write-Host "⚠ Erro ao remover função (pode não existir): $($_.Exception.Message)" -ForegroundColor Yellow
}

# Aguardar um pouco para garantir que a remoção foi processada
Write-Host "Aguardando 10 segundos para processamento..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Fazer deploy completo
Write-Host "=== FAZENDO DEPLOY COMPLETO ===" -ForegroundColor Green
Write-Host "Aguarde... isso pode levar vários minutos..." -ForegroundColor Cyan

try {
    # Deploy com flags extras para forçar rebuild
    serverless deploy --stage prod --verbose --force
    
    Write-Host ""
    Write-Host "=== DEPLOY CONCLUÍDO COM SUCESSO! ===" -ForegroundColor Green
    Write-Host "A função Lambda foi completamente reconstruída com as dependências corretas." -ForegroundColor Green
    Write-Host ""
    Write-Host "Para testar:" -ForegroundColor Cyan
    Write-Host "1. Aguarde 2-3 minutos para a função inicializar" -ForegroundColor Gray
    Write-Host "2. Teste o endpoint: https://[seu-endpoint]/" -ForegroundColor Gray
    Write-Host "3. Verifique os logs no CloudWatch" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "=== ERRO NO DEPLOY ===" -ForegroundColor Red
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "1. Verifique se o Docker está rodando" -ForegroundColor Gray
    Write-Host "2. Verifique suas credenciais AWS" -ForegroundColor Gray
    Write-Host "3. Tente: serverless deploy --stage prod --verbose" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "=== SCRIPT FINALIZADO ===" -ForegroundColor Green

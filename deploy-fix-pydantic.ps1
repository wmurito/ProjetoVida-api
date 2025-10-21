# Script para corrigir o erro de pydantic_core no Lambda
# Execute este script para fazer o deploy com as dependências corrigidas

Write-Host "=== CORRIGINDO ERRO PYDANTIC_CORE NO LAMBDA ===" -ForegroundColor Green
Write-Host ""

# Verificar se o serverless está instalado
Write-Host "Verificando se o Serverless Framework está instalado..." -ForegroundColor Yellow
try {
    $serverlessVersion = serverless --version
    Write-Host "✓ Serverless Framework encontrado: $serverlessVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Serverless Framework não encontrado. Instalando..." -ForegroundColor Red
    npm install -g serverless
    npm install -g serverless-python-requirements
}

Write-Host ""
Write-Host "=== LIMPANDO CACHE E ARQUIVOS TEMPORÁRIOS ===" -ForegroundColor Yellow

# Limpar cache do serverless
if (Test-Path ".serverless") {
    Remove-Item -Recurse -Force ".serverless"
    Write-Host "✓ Cache do serverless removido" -ForegroundColor Green
}

# Limpar node_modules se existir
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "✓ node_modules removido" -ForegroundColor Green
}

# Limpar arquivos Python compilados
Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object { Remove-Item $_ -Force }
Get-ChildItem -Path . -Recurse -Name "__pycache__" | ForEach-Object { Remove-Item $_ -Recurse -Force }
Write-Host "✓ Arquivos Python compilados removidos" -ForegroundColor Green

Write-Host ""
Write-Host "=== VERIFICANDO ARQUIVOS DE DEPENDÊNCIAS ===" -ForegroundColor Yellow

# Verificar se requirements-lambda.txt existe
if (Test-Path "requirements-lambda.txt") {
    Write-Host "✓ requirements-lambda.txt encontrado" -ForegroundColor Green
    Write-Host "Conteúdo do arquivo:" -ForegroundColor Cyan
    Get-Content "requirements-lambda.txt" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "✗ requirements-lambda.txt não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== FAZENDO DEPLOY PARA LAMBDA ===" -ForegroundColor Yellow
Write-Host "Aguarde... isso pode levar alguns minutos..." -ForegroundColor Cyan

# Fazer deploy
try {
    serverless deploy --stage prod --verbose
    Write-Host ""
    Write-Host "=== DEPLOY CONCLUÍDO COM SUCESSO! ===" -ForegroundColor Green
    Write-Host "A API foi atualizada com as dependências corrigidas." -ForegroundColor Green
    Write-Host ""
    Write-Host "Para testar a API, você pode usar:" -ForegroundColor Cyan
    Write-Host "  - Endpoint: https://[seu-endpoint]/" -ForegroundColor Gray
    Write-Host "  - Status: https://[seu-endpoint]/" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "=== ERRO NO DEPLOY ===" -ForegroundColor Red
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "1. Verifique se você tem permissões AWS configuradas" -ForegroundColor Gray
    Write-Host "2. Verifique se o Docker está rodando (necessário para dockerizePip)" -ForegroundColor Gray
    Write-Host "3. Tente executar: serverless deploy --stage prod --verbose" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "=== SCRIPT FINALIZADO ===" -ForegroundColor Green

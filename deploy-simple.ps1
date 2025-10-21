# Script simples para deploy sem conflitos de dependências
# Removido pydantic-settings que não é usado no código

Write-Host "=== DEPLOY SIMPLES SEM CONFLITOS ===" -ForegroundColor Green
Write-Host "Removido pydantic-settings (não usado no código)" -ForegroundColor Cyan
Write-Host ""

# 1. Limpar cache
Write-Host "1. Limpando cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".serverless" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
Write-Host "✓ Cache limpo" -ForegroundColor Green

# 2. Verificar requirements
Write-Host "2. Verificando requirements..." -ForegroundColor Yellow
Write-Host "Dependências principais:" -ForegroundColor Cyan
Get-Content "requirements-lambda.txt" | Where-Object { $_ -like "*pydantic*" -or $_ -like "*fastapi*" -or $_ -like "*mangum*" } | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# 3. Deploy direto
Write-Host "3. Fazendo deploy..." -ForegroundColor Yellow
Write-Host "   Aguarde..." -ForegroundColor Cyan
serverless deploy --stage prod --verbose

Write-Host ""
Write-Host "=== DEPLOY CONCLUÍDO! ===" -ForegroundColor Green
Write-Host "Teste sua API em alguns minutos." -ForegroundColor Cyan

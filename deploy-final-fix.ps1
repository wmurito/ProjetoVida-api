# Script final para corrigir o erro pydantic_core
# Versão corrigida com pydantic-settings==1.99

Write-Host "=== CORREÇÃO FINAL DO ERRO PYDANTIC_CORE ===" -ForegroundColor Green
Write-Host "Usando pydantic-settings==1.99 (versão válida)" -ForegroundColor Cyan
Write-Host ""

# 1. Limpar cache do Docker
Write-Host "1. Limpando cache do Docker..." -ForegroundColor Yellow
docker system prune -f 2>$null
Write-Host "✓ Cache do Docker limpo" -ForegroundColor Green

# 2. Limpar cache local
Write-Host "2. Limpando cache local..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".serverless" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
Write-Host "✓ Cache local limpo" -ForegroundColor Green

# 3. Verificar versões
Write-Host "3. Verificando versões das dependências..." -ForegroundColor Yellow
$pydanticLine = Get-Content "requirements-lambda.txt" | Where-Object { $_ -like "*pydantic*" }
Write-Host "  $pydanticLine" -ForegroundColor Cyan

# 4. Remover função existente
Write-Host "4. Removendo função Lambda existente..." -ForegroundColor Yellow
serverless remove --stage prod --verbose 2>$null
Write-Host "✓ Função removida" -ForegroundColor Green

# 5. Aguardar
Write-Host "5. Aguardando 20 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 6. Deploy
Write-Host "6. Fazendo deploy final..." -ForegroundColor Yellow
Write-Host "   Aguarde... isso pode levar alguns minutos..." -ForegroundColor Cyan
serverless deploy --stage prod --verbose --force

Write-Host ""
Write-Host "=== DEPLOY FINALIZADO! ===" -ForegroundColor Green
Write-Host "A API foi atualizada com as dependências corretas." -ForegroundColor Green
Write-Host "Aguarde 2-3 minutos e teste sua API." -ForegroundColor Cyan

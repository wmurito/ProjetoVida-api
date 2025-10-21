# Script para corrigir o problema CORS
# Alterado de httpApi para http (API Gateway v1) para melhor suporte CORS

Write-Host "=== CORRIGINDO PROBLEMA CORS ===" -ForegroundColor Green
Write-Host "Alterado de httpApi para http (API Gateway v1)" -ForegroundColor Cyan
Write-Host ""

# 1. Limpar cache
Write-Host "1. Limpando cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".serverless" -ErrorAction SilentlyContinue
Write-Host "✓ Cache limpo" -ForegroundColor Green

# 2. Deploy com correção CORS
Write-Host "2. Fazendo deploy com correção CORS..." -ForegroundColor Yellow
Write-Host "   Aguarde... isso pode levar alguns minutos..." -ForegroundColor Cyan
serverless deploy --stage prod --verbose

Write-Host ""
Write-Host "=== DEPLOY CORS CONCLUÍDO! ===" -ForegroundColor Green
Write-Host "A API agora deve aceitar requisições do frontend." -ForegroundColor Green
Write-Host "Teste o dashboard em alguns minutos." -ForegroundColor Cyan
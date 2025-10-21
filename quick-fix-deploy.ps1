# Script rápido para corrigir o erro pydantic_core
# Execute este script para resolver definitivamente o problema

Write-Host "=== CORREÇÃO RÁPIDA DO ERRO PYDANTIC_CORE ===" -ForegroundColor Green
Write-Host ""

# 1. Limpar tudo
Write-Host "1. Limpando cache e arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".serverless" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
Write-Host "✓ Limpeza concluída" -ForegroundColor Green

# 2. Remover função Lambda existente
Write-Host "2. Removendo função Lambda existente..." -ForegroundColor Yellow
serverless remove --stage prod --verbose 2>$null
Write-Host "✓ Função removida" -ForegroundColor Green

# 3. Aguardar
Write-Host "3. Aguardando 15 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 4. Deploy com força
Write-Host "4. Fazendo deploy com força..." -ForegroundColor Yellow
serverless deploy --stage prod --verbose --force

Write-Host ""
Write-Host "=== DEPLOY CONCLUÍDO! ===" -ForegroundColor Green
Write-Host "Aguarde 2-3 minutos e teste sua API." -ForegroundColor Cyan

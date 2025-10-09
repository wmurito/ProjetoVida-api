# Script de Deploy Limpo
Write-Host "Limpando arquivos temporarios..." -ForegroundColor Yellow

# Remover pasta .serverless se existir
if (Test-Path ".serverless") {
    Remove-Item -Recurse -Force .serverless
}

# Remover arquivos zip antigos
Remove-Item -Force *.zip -ErrorAction SilentlyContinue

Write-Host "Iniciando deploy..." -ForegroundColor Green
serverless deploy --stage prod --verbose

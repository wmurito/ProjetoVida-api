# Script para limpar arquivos desnecessários antes do deploy
Write-Host "🧹 Limpando arquivos desnecessários para deploy..." -ForegroundColor Green

# Remover arquivos de cache Python
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
    Write-Host "✅ Removido __pycache__" -ForegroundColor Yellow
}

# Remover arquivos .pyc
Get-ChildItem -Recurse -Name "*.pyc" | ForEach-Object {
    Remove-Item $_ -Force
    Write-Host "✅ Removido $($_)" -ForegroundColor Yellow
}

# Remover arquivos de log
Get-ChildItem -Name "*.log" | ForEach-Object {
    Remove-Item $_ -Force
    Write-Host "✅ Removido $($_)" -ForegroundColor Yellow
}

# Remover arquivos temporários
if (Test-Path ".pytest_cache") {
    Remove-Item -Recurse -Force ".pytest_cache"
    Write-Host "✅ Removido .pytest_cache" -ForegroundColor Yellow
}

# Remover arquivos de cobertura
if (Test-Path "coverage") {
    Remove-Item -Recurse -Force "coverage"
    Write-Host "✅ Removido coverage" -ForegroundColor Yellow
}

if (Test-Path ".coverage") {
    Remove-Item -Force ".coverage"
    Write-Host "✅ Removido .coverage" -ForegroundColor Yellow
}

if (Test-Path "htmlcov") {
    Remove-Item -Recurse -Force "htmlcov"
    Write-Host "✅ Removido htmlcov" -ForegroundColor Yellow
}

# Remover arquivos do sistema
if (Test-Path ".DS_Store") {
    Remove-Item -Force ".DS_Store"
    Write-Host "✅ Removido .DS_Store" -ForegroundColor Yellow
}

if (Test-Path "Thumbs.db") {
    Remove-Item -Force "Thumbs.db"
    Write-Host "✅ Removido Thumbs.db" -ForegroundColor Yellow
}

# Remover arquivos .serverless antigos
if (Test-Path ".serverless") {
    Remove-Item -Recurse -Force ".serverless"
    Write-Host "✅ Removido .serverless" -ForegroundColor Yellow
}

Write-Host "🎉 Limpeza concluída! Arquivos desnecessários removidos." -ForegroundColor Green
Write-Host "📦 Tamanho do pacote otimizado para deploy." -ForegroundColor Cyan

# Script de Deploy para AWS Lambda - Projeto Vida (PowerShell)
# Deploy otimizado excluindo arquivos desnecessarios

param(
    [string]$Stage = "prod",
    [switch]$SkipDependencies = $false
)

# Configurar para parar em caso de erro
$ErrorActionPreference = "Stop"

Write-Host "Iniciando deploy da API para AWS Lambda..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Verificar se o Serverless Framework esta instalado
try {
    $null = Get-Command serverless -ErrorAction Stop
    Write-Host "Serverless Framework encontrado" -ForegroundColor Green
} catch {
    Write-Host "Serverless Framework nao encontrado!" -ForegroundColor Red
    Write-Host "Instalando Serverless Framework..." -ForegroundColor Yellow
    npm install -g serverless
}

# Verificar se as dependencias Python estao instaladas
if (-not $SkipDependencies) {
    Write-Host "Verificando dependencias Python..." -ForegroundColor Yellow
    
    if (-not (Test-Path "venv")) {
        Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Verificar se o AWS CLI esta configurado
Write-Host "Verificando configuracao AWS..." -ForegroundColor Yellow
try {
    $null = aws sts get-caller-identity 2>$null
    Write-Host "AWS CLI configurado" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI nao configurado!" -ForegroundColor Red
    Write-Host "Configure o AWS CLI com: aws configure" -ForegroundColor Yellow
    exit 1
}

# Limpar arquivos desnecessarios antes do deploy
Write-Host "Limpando arquivos desnecessarios..." -ForegroundColor Yellow

# Remover arquivos Python compilados
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Name "*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Name ".DS_Store" | Remove-Item -Force -ErrorAction SilentlyContinue

# Verificar se existe arquivo de parametros
if (-not (Test-Path "params.json")) {
    Write-Host "Arquivo params.json nao encontrado!" -ForegroundColor Yellow
    Write-Host "Criando arquivo de parametros padrao..." -ForegroundColor Yellow
    
    $paramsContent = @"
{
  "s3Bucket": "projeto-vida-prd",
  "s3KeyPrefix": "dashboard_files",
  "dbSecretName": "projeto-vida/database",
  "cognitoSecretName": "projeto-vida/cognito",
  "awsRegion": "us-east-1"
}
"@
    
    $paramsContent | Out-File -FilePath "params.json" -Encoding UTF8
    Write-Host "Arquivo params.json criado com valores padrao" -ForegroundColor Green
    Write-Host "Ajuste os valores conforme necessario antes do deploy" -ForegroundColor Yellow
}

# Fazer deploy usando o arquivo de producao
Write-Host "Fazendo deploy para producao..." -ForegroundColor Green
serverless deploy --config serverless-prod.yml --stage $Stage --verbose

Write-Host ""
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "Informacoes do deploy:" -ForegroundColor Cyan
Write-Host "   • Stage: $Stage" -ForegroundColor White
Write-Host "   • Runtime: Python 3.11" -ForegroundColor White
Write-Host "   • Memory: 1024MB" -ForegroundColor White
Write-Host "   • Timeout: 30s" -ForegroundColor White
Write-Host "   • Arquivos excluidos: Documentacao, testes, debug" -ForegroundColor White
Write-Host ""
Write-Host "Endpoints disponiveis:" -ForegroundColor Cyan
Write-Host "   • API: https://[seu-dominio]/" -ForegroundColor White
Write-Host "   • Teste: https://[seu-dominio]/test" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "   1. Testar os endpoints" -ForegroundColor White
Write-Host "   2. Configurar dominio personalizado (opcional)" -ForegroundColor White
Write-Host "   3. Configurar monitoramento" -ForegroundColor White
Write-Host ""
Write-Host "Deploy finalizado!" -ForegroundColor Green
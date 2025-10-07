# Script de Deploy Simples para AWS Lambda
param([string]$Stage = "prod")

Write-Host "Iniciando deploy da API para AWS Lambda..." -ForegroundColor Green

# Verificar se o Serverless Framework esta instalado
try {
    $null = Get-Command serverless -ErrorAction Stop
    Write-Host "Serverless Framework encontrado" -ForegroundColor Green
} catch {
    Write-Host "Serverless Framework nao encontrado! Instalando..." -ForegroundColor Yellow
    npm install -g serverless
}

# Verificar se o AWS CLI esta configurado
try {
    $null = aws sts get-caller-identity 2>$null
    Write-Host "AWS CLI configurado" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI nao configurado! Configure com: aws configure" -ForegroundColor Red
    exit 1
}

# Fazer deploy
Write-Host "Fazendo deploy para producao..." -ForegroundColor Green
serverless deploy --config serverless-prod.yml --stage $Stage --verbose

Write-Host "Deploy concluido!" -ForegroundColor Green

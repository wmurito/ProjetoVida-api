# 🚀 Script de Deploy para AWS Lambda - Projeto Vida (PowerShell)
# Deploy otimizado excluindo arquivos desnecessários

param(
    [string]$Stage = "prod",
    [switch]$SkipDependencies = $false
)

# Configurar para parar em caso de erro
$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando deploy da API para AWS Lambda..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Verificar se o Serverless Framework está instalado
try {
    $null = Get-Command serverless -ErrorAction Stop
    Write-Host "✅ Serverless Framework encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Serverless Framework não encontrado!" -ForegroundColor Red
    Write-Host "📦 Instalando Serverless Framework..." -ForegroundColor Yellow
    npm install -g serverless
}

# Verificar se as dependências Python estão instaladas
if (-not $SkipDependencies) {
    Write-Host "📦 Verificando dependências Python..." -ForegroundColor Yellow
    
    if (-not (Test-Path "venv")) {
        Write-Host "🔧 Criando ambiente virtual..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Verificar se o AWS CLI está configurado
Write-Host "🔍 Verificando configuração AWS..." -ForegroundColor Yellow
try {
    $null = aws sts get-caller-identity 2>$null
    Write-Host "✅ AWS CLI configurado" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI não configurado!" -ForegroundColor Red
    Write-Host "🔧 Configure o AWS CLI com: aws configure" -ForegroundColor Yellow
    exit 1
}

# Limpar arquivos desnecessários antes do deploy
Write-Host "🧹 Limpando arquivos desnecessários..." -ForegroundColor Yellow

# Remover arquivos Python compilados
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Name "*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Name ".DS_Store" | Remove-Item -Force -ErrorAction SilentlyContinue

# Verificar se existe arquivo de parâmetros
if (-not (Test-Path "params.json")) {
    Write-Host "⚠️  Arquivo params.json não encontrado!" -ForegroundColor Yellow
    Write-Host "📝 Criando arquivo de parâmetros padrão..." -ForegroundColor Yellow
    
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
    Write-Host "✅ Arquivo params.json criado com valores padrão" -ForegroundColor Green
    Write-Host "🔧 Ajuste os valores conforme necessário antes do deploy" -ForegroundColor Yellow
}

# Fazer deploy usando o arquivo de produção
Write-Host "🚀 Fazendo deploy para produção..." -ForegroundColor Green
serverless deploy --config serverless-prod.yml --stage $Stage --verbose

Write-Host ""
Write-Host "🎉 Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "📊 Informações do deploy:" -ForegroundColor Cyan
Write-Host "   • Stage: $Stage" -ForegroundColor White
Write-Host "   • Runtime: Python 3.11" -ForegroundColor White
Write-Host "   • Memory: 1024MB" -ForegroundColor White
Write-Host "   • Timeout: 30s" -ForegroundColor White
Write-Host "   • Arquivos excluídos: Documentação, testes, debug" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Endpoints disponíveis:" -ForegroundColor Cyan
Write-Host "   • API: https://[seu-dominio]/" -ForegroundColor White
Write-Host "   • Teste: https://[seu-dominio]/test" -ForegroundColor White
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Testar os endpoints" -ForegroundColor White
Write-Host "   2. Configurar domínio personalizado (opcional)" -ForegroundColor White
Write-Host "   3. Configurar monitoramento" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deploy finalizado!" -ForegroundColor Green

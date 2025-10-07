# Script de Deploy Universal para AWS Lambda
# Funciona de qualquer diretorio

param([string]$Stage = "prod")

# Obter o diretorio do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Mudar para o diretorio do projeto
Set-Location $ScriptDir

Write-Host "Deploy da API para AWS Lambda..." -ForegroundColor Green
Write-Host "Diretorio: $ScriptDir" -ForegroundColor Cyan

# Verificar se o Serverless Framework esta instalado
try {
    $null = Get-Command serverless -ErrorAction Stop
    Write-Host "✓ Serverless Framework encontrado" -ForegroundColor Green
} catch {
    Write-Host "✗ Serverless Framework nao encontrado! Instalando..." -ForegroundColor Yellow
    npm install -g serverless
}

# Verificar se o AWS CLI esta configurado
try {
    $null = aws sts get-caller-identity 2>$null
    Write-Host "✓ AWS CLI configurado" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI nao configurado!" -ForegroundColor Red
    Write-Host "Configure com: aws configure" -ForegroundColor Yellow
    exit 1
}

# Verificar se existe arquivo de parametros
if (-not (Test-Path "params.json")) {
    Write-Host "⚠ Arquivo params.json nao encontrado!" -ForegroundColor Yellow
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
    Write-Host "✓ Arquivo params.json criado" -ForegroundColor Green
}

# Fazer deploy
Write-Host "🚀 Fazendo deploy para producao..." -ForegroundColor Green
serverless deploy --config serverless-prod.yml --stage $Stage --verbose

Write-Host ""
Write-Host "🎉 Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "📊 Configuracoes:" -ForegroundColor Cyan
Write-Host "   • Stage: $Stage" -ForegroundColor White
Write-Host "   • Runtime: Python 3.11" -ForegroundColor White
Write-Host "   • Memory: 1024MB" -ForegroundColor White
Write-Host "   • Timeout: 30s" -ForegroundColor White
Write-Host "   • Arquivos excluidos: Documentacao, testes, debug" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deploy finalizado!" -ForegroundColor Green

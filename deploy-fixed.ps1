# Script de Deploy Corrigido para AWS Lambda
param([string]$Stage = "prod")

Write-Host "Deploy da API para AWS Lambda (Versao Corrigida)..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

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

# Limpar stack anterior se existir
Write-Host "🧹 Limpando stack anterior (se existir)..." -ForegroundColor Yellow
try {
    serverless remove --config serverless-prod.yml --stage $Stage --verbose 2>$null
    Write-Host "✓ Stack anterior removido" -ForegroundColor Green
} catch {
    Write-Host "ℹ Nenhum stack anterior encontrado" -ForegroundColor Cyan
}

# Aguardar um pouco para garantir que o stack foi removido
Start-Sleep -Seconds 5

# Fazer deploy
Write-Host "🚀 Fazendo deploy para producao..." -ForegroundColor Green
Write-Host "Configuracoes:" -ForegroundColor Cyan
Write-Host "  • Runtime: Python 3.11" -ForegroundColor White
Write-Host "  • Memory: 1024MB" -ForegroundColor White
Write-Host "  • Timeout: 29s" -ForegroundColor White
Write-Host "  • Stage: $Stage" -ForegroundColor White
Write-Host "  • Regiao: us-east-1" -ForegroundColor White
Write-Host ""

serverless deploy --config serverless-prod.yml --stage $Stage --verbose

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Deploy concluido com sucesso!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "📊 Configuracoes aplicadas:" -ForegroundColor Cyan
    Write-Host "   • Runtime: Python 3.11" -ForegroundColor White
    Write-Host "   • Memory: 1024MB" -ForegroundColor White
    Write-Host "   • Timeout: 29s" -ForegroundColor White
    Write-Host "   • Concorrencia provisionada: 2 instancias" -ForegroundColor White
    Write-Host "   • Arquivos excluidos: Documentacao, testes, debug" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ Deploy finalizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Deploy falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima para mais detalhes." -ForegroundColor Yellow
}

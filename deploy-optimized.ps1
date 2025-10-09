# Script de deploy otimizado para resolver problema de tamanho
Write-Host "🚀 Iniciando deploy otimizado do ProjetoVida API..." -ForegroundColor Green

# 1. Limpar arquivos desnecessários
Write-Host "`n🧹 Passo 1: Limpando arquivos desnecessários..." -ForegroundColor Yellow
& .\cleanup-for-deploy.ps1

# 2. Verificar tamanho do diretório
Write-Host "`n📊 Passo 2: Verificando tamanho do diretório..." -ForegroundColor Yellow
$size = (Get-ChildItem -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Tamanho atual: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan

# 3. Deploy com configurações otimizadas
Write-Host "`n🚀 Passo 3: Executando deploy otimizado..." -ForegroundColor Yellow
Write-Host "Usando requirements-lambda.txt otimizado..." -ForegroundColor Cyan

# Deploy com verbose para monitorar
npm run deploy:prod

# 4. Verificar status do deploy
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host "🌐 API disponível em: https://84i83ihklg.execute-api.us-east-1.amazonaws.com" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Deploy falhou. Verifique os logs acima." -ForegroundColor Red
    Write-Host "💡 Dicas para resolver:" -ForegroundColor Yellow
    Write-Host "   - Verifique se todas as dependências estão no requirements-lambda.txt" -ForegroundColor White
    Write-Host "   - Confirme se os arquivos desnecessários foram removidos" -ForegroundColor White
    Write-Host "   - Verifique se o serverless.yml está configurado corretamente" -ForegroundColor White
}

Write-Host "`n🎯 Deploy otimizado finalizado!" -ForegroundColor Green

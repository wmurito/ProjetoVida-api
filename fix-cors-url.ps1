# Script para corrigir o problema de CORS - URL da API
Write-Host "🔧 Corrigindo problema de CORS..." -ForegroundColor Yellow

# Verificar se estamos no diretório correto
if (-not (Test-Path "serverless.yml")) {
    Write-Host "❌ Execute este script no diretório ProjetoVida-api" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Problema identificado:" -ForegroundColor Cyan
Write-Host "   Frontend usando: https://80alai4x6c.execute-api.us-east-1.amazonaws.com" -ForegroundColor Red
Write-Host "   API configurada: https://pteq15e8a6.execute-api.us-east-1.amazonaws.com" -ForegroundColor Green

Write-Host "`n🚀 Soluções disponíveis:" -ForegroundColor Yellow
Write-Host "1. Fazer deploy da API atual (pteq15e8a6) - RECOMENDADO" -ForegroundColor Green
Write-Host "2. Atualizar CORS para aceitar a nova URL (80alai4x6c)" -ForegroundColor Yellow

$escolha = Read-Host "`nEscolha uma opção (1 ou 2)"

if ($escolha -eq "1") {
    Write-Host "`n🚀 Fazendo deploy da API com CORS configurado..." -ForegroundColor Green
    
    # Verificar se serverless está instalado
    if (-not (Get-Command serverless -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Serverless Framework não encontrado. Instalando..." -ForegroundColor Red
        npm install -g serverless
    }
    
    # Fazer deploy
    Write-Host "📦 Fazendo deploy..." -ForegroundColor Yellow
    serverless deploy --stage prod --verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
        Write-Host "🔗 URL da API: https://pteq15e8a6.execute-api.us-east-1.amazonaws.com" -ForegroundColor Cyan
        Write-Host "`n📝 PRÓXIMO PASSO:" -ForegroundColor Yellow
        Write-Host "   Configure a variável VITE_API_URL no Amplify Console:" -ForegroundColor White
        Write-Host "   https://pteq15e8a6.execute-api.us-east-1.amazonaws.com" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
    }
    
} elseif ($escolha -eq "2") {
    Write-Host "`n🔧 Atualizando CORS para aceitar a nova URL..." -ForegroundColor Yellow
    
    # Atualizar serverless.yml para incluir a nova URL
    $serverlessContent = Get-Content "serverless.yml" -Raw
    $newServerlessContent = $serverlessContent -replace "https://master\.d1yi28nqqe44f2\.amplifyapp\.com", "https://master.d1yi28nqqe44f2.amplifyapp.com`n              - https://80alai4x6c.execute-api.us-east-1.amazonaws.com"
    
    Set-Content "serverless.yml" $newServerlessContent
    Write-Host "✅ serverless.yml atualizado" -ForegroundColor Green
    
    # Atualizar main.py
    $mainContent = Get-Content "main.py" -Raw
    $newMainContent = $mainContent -replace '"https://master\.d1yi28nqqe44f2\.amplifyapp\.com"', '"https://master.d1yi28nqqe44f2.amplifyapp.com", "https://80alai4x6c.execute-api.us-east-1.amazonaws.com"'
    
    Set-Content "main.py" $newMainContent
    Write-Host "✅ main.py atualizado" -ForegroundColor Green
    
    Write-Host "`n🚀 Fazendo deploy com nova configuração..." -ForegroundColor Yellow
    serverless deploy --stage prod --verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
        Write-Host "🔗 API agora aceita requisições de ambas as URLs" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ Opção inválida. Execute o script novamente." -ForegroundColor Red
}

Write-Host "`n📋 Para testar após o deploy:" -ForegroundColor Yellow
Write-Host "   curl -X OPTIONS https://pteq15e8a6.execute-api.us-east-1.amazonaws.com/dashboard/estadiamento \`" -ForegroundColor White
Write-Host "     -H 'Origin: https://master.d1yi28nqqe44f2.amplifyapp.com' \`" -ForegroundColor White
Write-Host "     -H 'Access-Control-Request-Method: GET' \`" -ForegroundColor White
Write-Host "     -H 'Access-Control-Request-Headers: authorization,content-type' \`" -ForegroundColor White
Write-Host "     -v" -ForegroundColor White

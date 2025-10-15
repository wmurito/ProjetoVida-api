# Script PowerShell para deploy da API com configuração CORS correta
Write-Host "🚀 Fazendo deploy da API com configuração CORS..." -ForegroundColor Green

# Verificar se serverless está instalado
try {
    $null = Get-Command serverless -ErrorAction Stop
    Write-Host "✅ Serverless CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Serverless CLI não encontrado. Instalando..." -ForegroundColor Red
    npm install -g serverless
}

# Verificar se estamos no diretório correto
if (-not (Test-Path "serverless.yml")) {
    Write-Host "❌ Arquivo serverless.yml não encontrado. Execute este script no diretório da API." -ForegroundColor Red
    exit 1
}

# Verificar configuração CORS
Write-Host "🔍 Verificando configuração CORS..." -ForegroundColor Yellow
$corsConfig = Get-Content "serverless.yml" | Select-String "https://master.d1yi28nqqe44f2.amplifyapp.com"
if ($corsConfig) {
    Write-Host "✅ CORS configurado corretamente para o domínio do Amplify" -ForegroundColor Green
} else {
    Write-Host "❌ CORS não configurado para o domínio do Amplify" -ForegroundColor Red
    exit 1
}

# Fazer deploy
Write-Host "🚀 Fazendo deploy da API..." -ForegroundColor Green
$deployResult = serverless deploy --stage prod

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host "🔗 Testando CORS..." -ForegroundColor Yellow
    
    # Testar CORS
    try {
        $headers = @{
            "Origin" = "https://master.d1yi28nqqe44f2.amplifyapp.com"
            "Access-Control-Request-Method" = "GET"
            "Access-Control-Request-Headers" = "Content-Type,Authorization"
        }
        
        $response = Invoke-WebRequest -Uri "https://pteq15e8a6.execute-api.us-east-1.amazonaws.com/" -Method OPTIONS -Headers $headers -UseBasicParsing
        Write-Host "✅ CORS testado com sucesso" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Erro ao testar CORS: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 API deployada com CORS configurado!" -ForegroundColor Green
    Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Teste a aplicação no Amplify" -ForegroundColor White
    Write-Host "   2. Verifique se os erros de CORS foram resolvidos" -ForegroundColor White
    Write-Host "   3. Monitore os logs da API se necessário" -ForegroundColor White
} else {
    Write-Host "❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
    exit 1
}


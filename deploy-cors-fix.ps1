# Script para fazer deploy da API com CORS corrigido
Write-Host "🚀 Fazendo deploy da API com CORS corrigido..." -ForegroundColor Green

# Verificar se estamos no diretório correto
if (-not (Test-Path "serverless.yml")) {
    Write-Host "❌ Execute este script no diretório ProjetoVida-api" -ForegroundColor Red
    Write-Host "📁 Diretório atual: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Configuração CORS corrigida no serverless.yml" -ForegroundColor Green
Write-Host "📋 Configuração aplicada:" -ForegroundColor Cyan
Write-Host "   - allowedOrigins: https://master.d1yi28nqqe44f2.amplifyapp.com" -ForegroundColor White
Write-Host "   - allowedMethods: GET, POST, PUT, DELETE, OPTIONS" -ForegroundColor White
Write-Host "   - allowCredentials: true" -ForegroundColor White

# Verificar se serverless está instalado
if (-not (Get-Command serverless -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Serverless Framework não encontrado. Instalando..." -ForegroundColor Red
    npm install -g serverless
}

Write-Host "`n📦 Iniciando deploy..." -ForegroundColor Yellow
Write-Host "⏳ Isso pode levar alguns minutos..." -ForegroundColor Yellow

# Fazer deploy
try {
    serverless deploy --stage prod --verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
        
        # Obter informações da API
        Write-Host "`n📋 Informações da API:" -ForegroundColor Cyan
        serverless info --stage prod
        
        Write-Host "`n🔗 URL da API: https://80alai4x6c.execute-api.us-east-1.amazonaws.com" -ForegroundColor Cyan
        Write-Host "🌐 CORS configurado para: https://master.d1yi28nqqe44f2.amplifyapp.com" -ForegroundColor Green
        
        Write-Host "`n🧪 Testando CORS..." -ForegroundColor Yellow
        
        # Testar CORS
        $testUrl = "https://80alai4x6c.execute-api.us-east-1.amazonaws.com/dashboard/estadiamento"
        $origin = "https://master.d1yi28nqqe44f2.amplifyapp.com"
        
        Write-Host "Testando: $testUrl" -ForegroundColor White
        Write-Host "Origin: $origin" -ForegroundColor White
        
        # Fazer teste CORS
        try {
            $response = Invoke-WebRequest -Uri $testUrl -Method OPTIONS -Headers @{
                "Origin" = $origin
                "Access-Control-Request-Method" = "GET"
                "Access-Control-Request-Headers" = "authorization,content-type"
            } -UseBasicParsing
            
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ CORS funcionando corretamente!" -ForegroundColor Green
                Write-Host "📊 Status: $($response.StatusCode)" -ForegroundColor Green
            } else {
                Write-Host "⚠️ CORS retornou status: $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Erro ao testar CORS: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        Write-Host "`n📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
        Write-Host "1. ✅ API deployada com CORS configurado" -ForegroundColor Green
        Write-Host "2. 🔄 Recarregue sua aplicação no Amplify" -ForegroundColor White
        Write-Host "3. 🧪 Teste as funcionalidades do dashboard" -ForegroundColor White
        Write-Host "4. 📊 Verifique se os erros de CORS desapareceram" -ForegroundColor White
        
    } else {
        Write-Host "`n❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
        Write-Host "💡 Dicas para resolver:" -ForegroundColor Yellow
        Write-Host "   - Verifique se as credenciais AWS estão configuradas" -ForegroundColor White
        Write-Host "   - Verifique se tem permissões para deploy no AWS" -ForegroundColor White
        Write-Host "   - Verifique se a região us-east-1 está correta" -ForegroundColor White
    }
} catch {
    Write-Host "`n❌ Erro durante o deploy: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Para testar manualmente:" -ForegroundColor Yellow
Write-Host "curl -X OPTIONS https://80alai4x6c.execute-api.us-east-1.amazonaws.com/dashboard/estadiamento \`" -ForegroundColor White
Write-Host "  -H 'Origin: https://master.d1yi28nqqe44f2.amplifyapp.com' \`" -ForegroundColor White
Write-Host "  -H 'Access-Control-Request-Method: GET' \`" -ForegroundColor White
Write-Host "  -H 'Access-Control-Request-Headers: authorization,content-type' \`" -ForegroundColor White
Write-Host "  -v" -ForegroundColor White
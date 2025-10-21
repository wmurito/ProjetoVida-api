# Script para deploy final com CORS corrigido
Write-Host "🚀 Deploy Final - CORS Corrigido" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Verificar se estamos no diretório correto
if (-not (Test-Path "serverless.yml")) {
    Write-Host "❌ Execute este script no diretório ProjetoVida-api" -ForegroundColor Red
    Write-Host "📁 Diretório atual: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "📁 Conteúdo do diretório:" -ForegroundColor Yellow
    Get-ChildItem | Select-Object Name, Mode | Format-Table
    exit 1
}

Write-Host "✅ Diretório correto encontrado" -ForegroundColor Green
Write-Host "📋 Configurações aplicadas:" -ForegroundColor Cyan
Write-Host "   - Handler OPTIONS removido do main.py" -ForegroundColor White
Write-Host "   - CORS configurado no serverless.yml" -ForegroundColor White
Write-Host "   - Origem permitida: https://master.d1yi28nqqe44f2.amplifyapp.com" -ForegroundColor White

Write-Host "`n📦 Iniciando deploy forçado..." -ForegroundColor Yellow
Write-Host "⏳ Isso pode levar alguns minutos..." -ForegroundColor Yellow

# Fazer deploy forçado
try {
    $deployResult = serverless deploy --stage prod --force 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
        
        # Obter informações da API
        Write-Host "`n📋 Informações da API:" -ForegroundColor Cyan
        serverless info --stage prod
        
        Write-Host "`n🎯 CORS Configurado:" -ForegroundColor Green
        Write-Host "   - API Gateway HTTP API gerencia CORS automaticamente" -ForegroundColor White
        Write-Host "   - Requisições OPTIONS não chegam ao Lambda" -ForegroundColor White
        Write-Host "   - Headers CORS retornados pelo API Gateway" -ForegroundColor White
        
        Write-Host "`n🧪 Testando CORS..." -ForegroundColor Yellow
        
        # Teste simples de CORS
        $testUrl = "https://80alai4x6c.execute-api.us-east-1.amazonaws.com/dashboard/estadiamento"
        $origin = "https://master.d1yi28nqqe44f2.amplifyapp.com"
        
        try {
            Write-Host "Testando OPTIONS request..." -ForegroundColor White
            $response = Invoke-WebRequest -Uri $testUrl -Method OPTIONS -Headers @{
                "Origin" = $origin
                "Access-Control-Request-Method" = "GET"
                "Access-Control-Request-Headers" = "authorization,content-type"
            } -UseBasicParsing -TimeoutSec 10
            
            Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
            
            # Verificar headers CORS
            $corsHeaders = $response.Headers | Where-Object { $_.Key -like "*access-control*" }
            if ($corsHeaders) {
                Write-Host "✅ Headers CORS encontrados:" -ForegroundColor Green
                foreach ($header in $corsHeaders) {
                    Write-Host "   $($header.Key): $($header.Value)" -ForegroundColor White
                }
            } else {
                Write-Host "⚠️ Headers CORS não encontrados" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "❌ Erro ao testar CORS: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        Write-Host "`n📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
        Write-Host "1. ✅ API deployada com CORS corrigido" -ForegroundColor Green
        Write-Host "2. 🔄 Recarregue sua aplicação no Amplify" -ForegroundColor White
        Write-Host "3. 🧪 Teste as funcionalidades do dashboard" -ForegroundColor White
        Write-Host "4. 📊 Verifique se os erros de CORS desapareceram" -ForegroundColor White
        
        Write-Host "`n🎯 RESULTADO ESPERADO:" -ForegroundColor Cyan
        Write-Host "   - ✅ Requisições OPTIONS retornam 200 OK" -ForegroundColor Green
        Write-Host "   - ✅ Headers Access-Control-Allow-Origin presentes" -ForegroundColor Green
        Write-Host "   - ✅ Frontend consegue fazer requisições sem erro CORS" -ForegroundColor Green
        
    } else {
        Write-Host "`n❌ Erro no deploy:" -ForegroundColor Red
        Write-Host $deployResult -ForegroundColor Red
        
        Write-Host "`n💡 Dicas para resolver:" -ForegroundColor Yellow
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

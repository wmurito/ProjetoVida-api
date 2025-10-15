# Teste de CORS para ProjetoVida API
$url = "https://pteq15e8a6.execute-api.us-east-1.amazonaws.com/"
$origin = "https://master.d1yi28nqqe44f2.amplifyapp.com"

Write-Host "Testando CORS para: $url" -ForegroundColor Green
Write-Host "Origin: $origin" -ForegroundColor Yellow

# Teste OPTIONS (preflight)
Write-Host "`n=== Teste OPTIONS (Preflight) ===" -ForegroundColor Cyan
try {
    $headers = @{
        "Origin" = $origin
        "Access-Control-Request-Method" = "GET"
        "Access-Control-Request-Headers" = "Content-Type,Authorization"
    }
    
    $response = Invoke-WebRequest -Uri $url -Method OPTIONS -Headers $headers -TimeoutSec 10
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    
    Write-Host "`nHeaders CORS:" -ForegroundColor Yellow
    foreach ($header in $response.Headers.GetEnumerator()) {
        if ($header.Key -like "*Access-Control*") {
            Write-Host "  $($header.Key): $($header.Value)" -ForegroundColor White
        }
    }
    
    # Verificar se CORS está funcionando
    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]
    if ($allowOrigin -eq $origin) {
        Write-Host "`n✅ CORS OPTIONS funcionando!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ CORS OPTIONS com problema" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Erro no teste OPTIONS: $($_.Exception.Message)" -ForegroundColor Red
}

# Teste GET
Write-Host "`n=== Teste GET ===" -ForegroundColor Cyan
try {
    $headers = @{
        "Origin" = $origin
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri $url -Method GET -Headers $headers -TimeoutSec 10
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    
    Write-Host "`nHeaders CORS:" -ForegroundColor Yellow
    foreach ($header in $response.Headers.GetEnumerator()) {
        if ($header.Key -like "*Access-Control*") {
            Write-Host "  $($header.Key): $($header.Value)" -ForegroundColor White
        }
    }
    
    # Verificar se CORS está funcionando
    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]
    if ($allowOrigin -eq $origin) {
        Write-Host "`n✅ CORS GET funcionando!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ CORS GET com problema" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Erro no teste GET: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Teste Concluído ===" -ForegroundColor Magenta



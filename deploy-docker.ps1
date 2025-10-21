# Deploy usando Docker container image
Write-Host "=== Deploy com Docker Container ===" -ForegroundColor Cyan

Write-Host "`n=== Fazendo deploy ===" -ForegroundColor Cyan
npx serverless deploy --config serverless-docker.yml --stage prod --verbose

Write-Host "`n=== Concluído ===" -ForegroundColor Green
Write-Host "URL da API estará no output acima" -ForegroundColor Yellow

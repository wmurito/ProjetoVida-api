# Script para corrigir e fazer deploy da Lambda

Write-Host "=== Limpando cache e builds anteriores ===" -ForegroundColor Cyan
Remove-Item -Path .serverless -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path package-lock.json -Force -ErrorAction SilentlyContinue

Write-Host "`n=== Instalando dependências do Serverless ===" -ForegroundColor Cyan
npm install

Write-Host "`n=== Removendo layer antiga ===" -ForegroundColor Cyan
aws lambda delete-layer-version --layer-name projetovida-api-prod-python-requirements --version-number 1 2>$null

Write-Host "`n=== Fazendo deploy ===" -ForegroundColor Cyan
npx serverless deploy --verbose --force

Write-Host "`n=== Deploy concluído! ===" -ForegroundColor Green
Write-Host "Verifique a URL da API Gateway no output acima" -ForegroundColor Yellow

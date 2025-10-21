# Limpeza completa e deploy
Write-Host "=== Limpando tudo ===" -ForegroundColor Cyan
Remove-Item -Path .serverless -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path .requirements-cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\UnitedIncome\serverless-python-requirements" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n=== Instalando serverless ===" -ForegroundColor Cyan
npm install

Write-Host "`n=== Deploy ===" -ForegroundColor Cyan
npx serverless deploy --stage prod --verbose --force

Write-Host "`n=== Concluído ===" -ForegroundColor Green

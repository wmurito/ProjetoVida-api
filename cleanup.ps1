# Script para limpar arquivos desnecessários para deploy

Write-Host "🧹 Limpando arquivos desnecessários..." -ForegroundColor Cyan

$filesToRemove = @(
    # Documentação redundante
    "ANALISE_CRUD.md",
    "GUIA_MIGRACAO.md",
    "SEGURANCA.md",
    "TERMO_ACEITE_FLUXO.md",
    "DEPLOY_AWS_LAMBDA.md",
    "DEPLOY_RAPIDO.md",
    "QUICK_START_DEPLOY.md",
    
    # Scripts de deploy alternativos (mantendo apenas Serverless)
    "deploy-projeto-vida.ps1",
    "deploy.ps1",
    "deploy.sh",
    
    # Arquivos de exemplo
    ".env.example",
    "params.example.json",
    
    # Scripts de migração (já executados)
    "migrate_to_new_schema.py",
    "backup.sql",
    "create_views.sql"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removido: $file" -ForegroundColor Green
    }
}

Write-Host "`n✅ Limpeza concluída!" -ForegroundColor Green
Write-Host "`n📦 Arquivos mantidos para deploy:" -ForegroundColor Cyan
Write-Host "  - Código Python (*.py)" -ForegroundColor Gray
Write-Host "  - serverless.yml" -ForegroundColor Gray
Write-Host "  - package.json" -ForegroundColor Gray
Write-Host "  - requirements.txt" -ForegroundColor Gray
Write-Host "  - .gitignore" -ForegroundColor Gray
Write-Host "  - .dockerignore" -ForegroundColor Gray
Write-Host "  - setup-secrets.ps1" -ForegroundColor Gray
Write-Host "  - ENDPOINTS.md (referência)" -ForegroundColor Gray
Write-Host "  - DEPLOY_SERVERLESS.md (guia)" -ForegroundColor Gray
Write-Host "  - QUICK_DEPLOY.md (guia rápido)" -ForegroundColor Gray

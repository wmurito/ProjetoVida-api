# Script para configurar AWS Secrets Manager
# ProjetoVida API

param(
    [string]$DatabaseUrl,
    [string]$CognitoUserPoolId,
    [string]$CognitoAppClientId
)

$ErrorActionPreference = "Stop"

$AwsRegion = "us-east-1"
$DbSecretName = "projeto-vida/database"
$CognitoSecretName = "projeto-vida/cognito"

Write-Host "🔐 Configurando AWS Secrets Manager" -ForegroundColor Cyan

# Verificar parâmetros
if (-not $DatabaseUrl) {
    Write-Host "❌ DatabaseUrl não fornecido" -ForegroundColor Red
    Write-Host "Uso: .\setup-secrets.ps1 -DatabaseUrl 'postgresql://...' -CognitoUserPoolId 'us-east-1_xxx' -CognitoAppClientId 'xxx'" -ForegroundColor Yellow
    exit 1
}

if (-not $CognitoUserPoolId -or -not $CognitoAppClientId) {
    Write-Host "❌ Credenciais Cognito não fornecidas" -ForegroundColor Red
    exit 1
}

# Criar/Atualizar secret do banco de dados
Write-Host "`n📊 Configurando secret do banco de dados..." -ForegroundColor Yellow

$dbSecretValue = @{
    DATABASE_URL = $DatabaseUrl
} | ConvertTo-Json

try {
    # Tentar atualizar secret existente
    aws secretsmanager update-secret `
        --secret-id $DbSecretName `
        --secret-string $dbSecretValue `
        --region $AwsRegion `
        --no-cli-pager | Out-Null
    
    Write-Host "  ✓ Secret '$DbSecretName' atualizado" -ForegroundColor Green
} catch {
    # Criar novo secret
    try {
        aws secretsmanager create-secret `
            --name $DbSecretName `
            --description "Database credentials for ProjetoVida API" `
            --secret-string $dbSecretValue `
            --region $AwsRegion `
            --no-cli-pager | Out-Null
        
        Write-Host "  ✓ Secret '$DbSecretName' criado" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao criar/atualizar secret do banco" -ForegroundColor Red
        Write-Host "  $_" -ForegroundColor Red
    }
}

# Criar/Atualizar secret do Cognito
Write-Host "`n🔑 Configurando secret do Cognito..." -ForegroundColor Yellow

$cognitoSecretValue = @{
    COGNITO_USER_POOL_ID = $CognitoUserPoolId
    COGNITO_APP_CLIENT_ID = $CognitoAppClientId
} | ConvertTo-Json

try {
    # Tentar atualizar secret existente
    aws secretsmanager update-secret `
        --secret-id $CognitoSecretName `
        --secret-string $cognitoSecretValue `
        --region $AwsRegion `
        --no-cli-pager | Out-Null
    
    Write-Host "  ✓ Secret '$CognitoSecretName' atualizado" -ForegroundColor Green
} catch {
    # Criar novo secret
    try {
        aws secretsmanager create-secret `
            --name $CognitoSecretName `
            --description "Cognito credentials for ProjetoVida API" `
            --secret-string $cognitoSecretValue `
            --region $AwsRegion `
            --no-cli-pager | Out-Null
        
        Write-Host "  ✓ Secret '$CognitoSecretName' criado" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao criar/atualizar secret do Cognito" -ForegroundColor Red
        Write-Host "  $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Secrets configurados com sucesso!" -ForegroundColor Green

Write-Host "`n📋 Verificar secrets:" -ForegroundColor Cyan
Write-Host "  aws secretsmanager get-secret-value --secret-id $DbSecretName --region $AwsRegion" -ForegroundColor Gray
Write-Host "  aws secretsmanager get-secret-value --secret-id $CognitoSecretName --region $AwsRegion" -ForegroundColor Gray

Write-Host "`n⚠️  IMPORTANTE: Adicione permissão à Lambda Role para acessar secrets:" -ForegroundColor Yellow
Write-Host @"
aws iam put-role-policy \
  --role-name ProjetoVidaLambdaRole \
  --policy-name SecretsManagerAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:$AwsRegion:*:secret:projeto-vida/*"
      ]
    }]
  }'
"@ -ForegroundColor Gray

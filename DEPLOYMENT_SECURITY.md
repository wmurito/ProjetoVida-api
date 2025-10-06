# 🚀 Guia de Deploy Seguro - ProjetoVida API

## 📋 Checklist de Segurança Pré-Deploy

### ✅ Configuração de Ambiente

- [ ] **Variáveis de Ambiente**
  - [ ] Todas as credenciais em variáveis de ambiente
  - [ ] Nenhum secret hardcoded no código
  - [ ] Arquivo `.env` no `.gitignore`
  - [ ] Uso de AWS Secrets Manager ou similar

- [ ] **Banco de Dados**
  - [ ] Conexão SSL/TLS habilitada
  - [ ] Usuário com privilégios mínimos
  - [ ] Backup automático configurado
  - [ ] Logs de auditoria habilitados

- [ ] **AWS Cognito**
  - [ ] User Pool configurado corretamente
  - [ ] App Client com configurações seguras
  - [ ] Políticas de senha adequadas
  - [ ] MFA habilitado (se aplicável)

### ✅ Configuração de Segurança

- [ ] **CORS**
  - [ ] Origins específicos (não `*`)
  - [ ] Métodos específicos (não `*`)
  - [ ] Headers específicos (não `*`)

- [ ] **Rate Limiting**
  - [ ] Implementado e testado
  - [ ] Limites adequados para cada endpoint
  - [ ] Monitoramento de tentativas

- [ ] **Headers de Segurança**
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] X-XSS-Protection: 1; mode=block
  - [ ] Strict-Transport-Security (HTTPS)

### ✅ Logging e Monitoramento

- [ ] **Logs Seguros**
  - [ ] Nenhum token/senha em logs
  - [ ] Logs estruturados
  - [ ] Rotação de logs configurada
  - [ ] Retenção adequada

- [ ] **Monitoramento**
  - [ ] Alertas de segurança configurados
  - [ ] Métricas de performance
  - [ ] Logs de auditoria
  - [ ] Dashboard de segurança

## 🔧 Configurações de Produção

### 1. **Variáveis de Ambiente**

```bash
# Produção
ENVIRONMENT=production
STAGE=prod

# CORS restritivo
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
TRUSTED_HOSTS=yourdomain.com,www.yourdomain.com

# Logging
LOG_LEVEL=WARNING

# Segurança
MAX_UPLOAD_SIZE=5242880  # 5MB
REQUEST_TIMEOUT=30
```

### 2. **AWS Lambda Configuration**

```yaml
# serverless.yml
provider:
  name: aws
  runtime: python3.11
  stage: ${opt:stage, 'prod'}
  region: us-east-1
  
  environment:
    ENVIRONMENT: ${self:provider.stage}
    DATABASE_URL: ${ssm:/projetovida/${self:provider.stage}/database-url}
    COGNITO_USER_POOL_ID: ${ssm:/projetovida/${self:provider.stage}/cognito-user-pool-id}
    COGNITO_APP_CLIENT_ID: ${ssm:/projetovida/${self:provider.stage}/cognito-app-client-id}
  
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource: 
            - arn:aws:secretsmanager:${self:provider.region}:*:secret:projetovida/*
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
          Resource:
            - arn:aws:s3:::projetovida-uploads/*
```

### 3. **CloudFront Configuration**

```json
{
  "Comment": "ProjetoVida API CloudFront Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "api-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", // Managed-CachingDisabled
    "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf" // Managed-CORS-S3Origin
  },
  "Origins": [
    {
      "Id": "api-origin",
      "DomainName": "your-api-gateway-url.amazonaws.com",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }
  ],
  "Enabled": true,
  "HttpVersion": "http2",
  "PriceClass": "PriceClass_100"
}
```

## 🛡️ Configurações de Segurança

### 1. **WAF (Web Application Firewall)**

```yaml
# AWS WAF Rules
Rules:
  - Name: RateLimitRule
    Priority: 1
    Statement:
      RateBasedStatement:
        Limit: 2000
        AggregateKeyType: IP
    Action:
      Block: {}
  
  - Name: SQLInjectionRule
    Priority: 2
    Statement:
      ByteMatchStatement:
        SearchString: "union select"
        FieldToMatch:
          Body:
            OversizeHandling: CONTINUE
        TextTransformations:
          - Priority: 0
            Type: LOWERCASE
    Action:
      Block: {}
  
  - Name: XSSRule
    Priority: 3
    Statement:
      XssMatchStatement:
        FieldToMatch:
          AllQueryArguments: {}
        TextTransformations:
          - Priority: 0
            Type: URL_DECODE
    Action:
      Block: {}
```

### 2. **VPC Configuration**

```yaml
# VPC para Lambda
VPC:
  Type: AWS::EC2::VPC
  Properties:
    CidrBlock: 10.0.0.0/16
    EnableDnsHostnames: true
    EnableDnsSupport: true
    Tags:
      - Key: Name
        Value: ProjetoVida-VPC

PrivateSubnet:
  Type: AWS::EC2::Subnet
  Properties:
    VpcId: !Ref VPC
    CidrBlock: 10.0.1.0/24
    AvailabilityZone: !Select [0, !GetAZs '']
    Tags:
      - Key: Name
        Value: ProjetoVida-Private-Subnet
```

## 📊 Monitoramento e Alertas

### 1. **CloudWatch Alarms**

```yaml
# Alarmes de segurança
SecurityAlarms:
  - AlarmName: HighErrorRate
    MetricName: 4XXError
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 2
    
  - AlarmName: UnauthorizedAccess
    MetricName: 401Error
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 1
    
  - AlarmName: HighLatency
    MetricName: Duration
    Threshold: 5000  # 5 seconds
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 3
```

### 2. **Sentry Configuration**

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(auto_enabling_instrumentations=False),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development"),
)
```

## 🔄 Processo de Deploy

### 1. **Pre-Deploy Checklist**

```bash
#!/bin/bash
# pre-deploy.sh

echo "🔒 Executando verificações de segurança..."

# 1. Verificar secrets
python security_check.py
if [ $? -ne 0 ]; then
    echo "❌ Falha na verificação de segurança"
    exit 1
fi

# 2. Executar testes
python -m pytest security_tests.py -v
if [ $? -ne 0 ]; then
    echo "❌ Testes de segurança falharam"
    exit 1
fi

# 3. Verificar dependências
safety check
if [ $? -ne 0 ]; then
    echo "❌ Dependências vulneráveis encontradas"
    exit 1
fi

# 4. Verificar linting
flake8 . --max-line-length=88
if [ $? -ne 0 ]; then
    echo "❌ Problemas de linting encontrados"
    exit 1
fi

echo "✅ Todas as verificações passaram!"
```

### 2. **Deploy Script**

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando deploy seguro..."

# 1. Executar verificações pré-deploy
./pre-deploy.sh

# 2. Deploy para staging
echo "📦 Deploy para staging..."
serverless deploy --stage staging

# 3. Testes em staging
echo "🧪 Executando testes em staging..."
python -m pytest tests/ --env=staging

# 4. Deploy para produção
echo "🚀 Deploy para produção..."
serverless deploy --stage prod

# 5. Verificações pós-deploy
echo "✅ Verificações pós-deploy..."
curl -f https://api.yourdomain.com/health || exit 1

echo "🎉 Deploy concluído com sucesso!"
```

## 📋 Manutenção de Segurança

### 1. **Rotina Semanal**

- [ ] Verificar logs de segurança
- [ ] Atualizar dependências
- [ ] Revisar métricas de performance
- [ ] Verificar backups

### 2. **Rotina Mensal**

- [ ] Rotacionar chaves de API
- [ ] Revisar permissões IAM
- [ ] Atualizar certificados SSL
- [ ] Teste de recuperação de desastres

### 3. **Rotina Trimestral**

- [ ] Auditoria de segurança completa
- [ ] Teste de penetração
- [ ] Revisão de políticas de segurança
- [ ] Treinamento da equipe

## 🚨 Resposta a Incidentes

### 1. **Plano de Resposta**

```bash
# incident-response.sh
#!/bin/bash

echo "🚨 Iniciando resposta a incidente..."

# 1. Isolar o sistema
echo "🔒 Isolando sistema..."
# Implementar bloqueios necessários

# 2. Coletar evidências
echo "📊 Coletando evidências..."
# Coletar logs e métricas

# 3. Notificar equipe
echo "📢 Notificando equipe..."
# Enviar alertas

# 4. Implementar correções
echo "🔧 Implementando correções..."
# Aplicar patches de segurança

# 5. Monitorar recuperação
echo "👀 Monitorando recuperação..."
# Verificar se sistema está estável
```

### 2. **Contatos de Emergência**

- **Equipe de Segurança**: security@yourdomain.com
- **DevOps**: devops@yourdomain.com
- **Gerente de Projeto**: manager@yourdomain.com

## 📚 Recursos Adicionais

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://aws.amazon.com/security/security-resources/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security](https://python-security.readthedocs.io/)

---

**⚠️ Importante**: Este guia deve ser revisado e atualizado regularmente conforme novas ameaças e melhores práticas surgem.

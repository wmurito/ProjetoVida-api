# 🚀 Deploy com Serverless Framework + Docker

## 📋 Pré-requisitos

1. **Node.js** instalado (v18+)
2. **Docker Desktop** instalado e rodando
3. **AWS CLI** configurado
4. **Python 3.11** instalado

---

## 🔧 Passo 1: Instalar Dependências

```bash
# Instalar dependências Node.js
npm install

# Verificar instalação
npx serverless --version
```

---

## 🔐 Passo 2: Configurar Secrets (Primeira vez)

```powershell
.\setup-secrets.ps1 `
  -DatabaseUrl "postgresql://user:pass@rds-endpoint:5432/dbname" `
  -CognitoUserPoolId "us-east-1_h48q7uFnQ" `
  -CognitoAppClientId "q902jjsdui"
```

---

## 🚀 Passo 3: Deploy

### Deploy Completo

```bash
# Windows PowerShell
npm run deploy:prod

# Ou diretamente
npx serverless deploy --stage prod --verbose
```

### Deploy Rápido (apenas código)

```bash
npx serverless deploy function -f api --stage prod
```

---

## 📊 Comandos Úteis

### Ver informações do deploy

```bash
npx serverless info --stage prod
```

### Ver logs em tempo real

```bash
npm run logs

# Ou
npx serverless logs -f api -t --stage prod
```

### Invocar função

```bash
npx serverless invoke -f api --stage prod
```

### Remover stack completo

```bash
npx serverless remove --stage prod
```

---

## 🐳 Docker

O Serverless Framework usa Docker automaticamente para:
- ✅ Compilar dependências Python compatíveis com Lambda
- ✅ Garantir compatibilidade de bibliotecas nativas
- ✅ Criar layer otimizado

**Certifique-se que Docker Desktop está rodando antes do deploy!**

---

## 📁 Estrutura do Deploy

```
ProjetoVida-api/
├── serverless.yml          # Configuração principal
├── package.json            # Dependências Node.js
├── requirements.txt        # Dependências Python
├── main.py                 # Handler Lambda
├── *.py                    # Outros arquivos Python
└── .serverless/            # Gerado após deploy
    ├── cloudformation-template-*.json
    └── projetovida-api.zip
```

---

## ⚙️ Configuração (serverless.yml)

### Variáveis de Ambiente

```yaml
environment:
  AWS_REGION: us-east-1
  S3_BUCKET: projeto-vida-prd
  S3_KEY_PREFIX: dashboard_files
  DB_SECRET_NAME: projeto-vida/database
  COGNITO_SECRET_NAME: projeto-vida/cognito
  STAGE: prod
```

### VPC

```yaml
vpc:
  securityGroupIds:
    - sg-010ebae9343e8f422
  subnetIds:
    - subnet-0fcb4e5a4433397c3
    - subnet-045bdd15a0355fdbc
```

### Permissões IAM

```yaml
iam:
  role:
    statements:
      - Effect: Allow
        Action:
          - s3:GetObject
          - s3:PutObject
          - s3:DeleteObject
          - s3:HeadObject
        Resource: "arn:aws:s3:::projeto-vida-prd/*"
      - Effect: Allow
        Action:
          - secretsmanager:GetSecretValue
        Resource: "arn:aws:secretsmanager:us-east-1:*:secret:projeto-vida/*"
```

---

## 🔍 Verificar Deploy

### 1. Obter URL da API

```bash
npx serverless info --stage prod
```

Output:
```
endpoint: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com
```

### 2. Testar endpoint

```bash
curl https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/
```

### 3. Ver logs

```bash
npx serverless logs -f api --stage prod
```

---

## 🔄 Workflow de Desenvolvimento

### 1. Desenvolvimento Local

```bash
# Rodar localmente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testar Mudanças

```bash
# Fazer alterações no código
# Testar localmente
```

### 3. Deploy

```bash
# Deploy completo (primeira vez ou mudanças em serverless.yml)
npm run deploy:prod

# Deploy rápido (apenas código)
npx serverless deploy function -f api --stage prod
```

### 4. Verificar

```bash
# Ver logs
npm run logs

# Testar API
curl https://API_URL/
```

---

## 🐛 Troubleshooting

### Erro: "Docker not found"

```bash
# Verificar se Docker está rodando
docker --version
docker ps

# Iniciar Docker Desktop
```

### Erro: "Unable to import module 'main'"

```bash
# Limpar cache e redeployar
rm -rf .serverless
rm -rf node_modules
npm install
npm run deploy:prod
```

### Erro: "Rate exceeded"

```bash
# Aguardar alguns minutos e tentar novamente
# Ou aumentar timeout no serverless.yml
```

### Erro: "Cannot connect to database"

```bash
# Verificar secrets
aws secretsmanager get-secret-value --secret-id projeto-vida/database

# Verificar VPC configuration
# Security Group deve permitir conexão Lambda -> RDS
```

### Deploy muito lento

```bash
# Usar deploy de função (mais rápido)
npx serverless deploy function -f api --stage prod

# Ou habilitar cache do Docker
# Docker Desktop -> Settings -> Resources -> Enable caching
```

---

## 📦 Otimizações

### 1. Layer de Dependências

O Serverless cria automaticamente um layer com as dependências Python, reduzindo o tamanho do pacote principal.

### 2. Slim Package

```yaml
custom:
  pythonRequirements:
    slim: true  # Remove arquivos desnecessários
    strip: false  # Mantém símbolos de debug
```

### 3. Exclusões

```yaml
package:
  patterns:
    - '!tests/**'
    - '!*.md'
    - '!.git/**'
```

---

## 🎯 Comparação: Serverless vs Script Manual

| Aspecto | Serverless | Script Manual |
|---------|-----------|---------------|
| Setup inicial | Mais complexo | Mais simples |
| Deploy | 1 comando | Múltiplos passos |
| Rollback | Automático | Manual |
| Infraestrutura | CloudFormation | Manual |
| CI/CD | Fácil integração | Requer scripts |
| Logs | Integrado | AWS CLI |
| Custo | Mesmo | Mesmo |

---

## 💡 Dicas

1. **Use Docker**: Garante compatibilidade das dependências
2. **Cache**: Docker Desktop com cache habilitado acelera builds
3. **Deploy rápido**: Use `deploy function` para mudanças pequenas
4. **Logs**: Mantenha terminal com logs aberto durante testes
5. **Stages**: Use `dev`, `staging`, `prod` para ambientes diferentes

---

## 📝 Checklist de Deploy

- [ ] Docker Desktop instalado e rodando
- [ ] Node.js instalado
- [ ] AWS CLI configurado
- [ ] `npm install` executado
- [ ] Secrets configurados no AWS Secrets Manager
- [ ] RDS acessível pela VPC
- [ ] Security Group configurado
- [ ] S3 Bucket criado
- [ ] Deploy executado com sucesso
- [ ] URL da API obtida
- [ ] Endpoints testados
- [ ] Logs verificados

---

## 🚀 Deploy em 3 Comandos

```bash
# 1. Instalar
npm install

# 2. Configurar secrets (primeira vez)
.\setup-secrets.ps1 -DatabaseUrl "postgresql://..." -CognitoUserPoolId "..." -CognitoAppClientId "..."

# 3. Deploy
npm run deploy:prod
```

---

## 📞 Suporte

- Documentação Serverless: https://www.serverless.com/framework/docs
- Plugin Python Requirements: https://github.com/serverless/serverless-python-requirements
- AWS Lambda: https://docs.aws.amazon.com/lambda/

---

## 💰 Custos

Mesmos custos do deploy manual (~$20/mês), sem custos adicionais do Serverless Framework (é gratuito para uso básico).

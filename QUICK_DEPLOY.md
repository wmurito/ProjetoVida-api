# ⚡ Deploy Rápido - 3 Comandos

## 🚀 Opção 1: Serverless Framework + Docker (Recomendado)

### Pré-requisitos
- ✅ Docker Desktop rodando
- ✅ Node.js instalado
- ✅ AWS CLI configurado

### Deploy

```bash
# 1. Instalar dependências
npm install

# 2. Configurar secrets (primeira vez)
.\setup-secrets.ps1 `
  -DatabaseUrl "postgresql://user:pass@endpoint:5432/db" `
  -CognitoUserPoolId "us-east-1_h48q7uFnQ" `
  -CognitoAppClientId "q902jjsdui"

# 3. Deploy
npm run deploy:prod
```

**Pronto!** 🎉

URL da API será exibida no final do deploy.

---

## 🔄 Atualizar Código

```bash
# Deploy completo (mudanças em serverless.yml)
npm run deploy:prod

# Deploy rápido (apenas código)
npx serverless deploy function -f api --stage prod
```

---

## 📊 Ver Logs

```bash
npm run logs
```

---

## 🆘 Troubleshooting

### Docker não está rodando
```bash
# Iniciar Docker Desktop e tentar novamente
```

### Erro de permissão AWS
```bash
aws configure
# Inserir suas credenciais
```

### Deploy muito lento
```bash
# Usar deploy de função (mais rápido)
npx serverless deploy function -f api --stage prod
```

---

## 📝 Comandos Úteis

```bash
# Ver informações do deploy
npx serverless info --stage prod

# Testar API
curl https://API_URL/

# Ver logs em tempo real
npm run logs

# Remover tudo
npx serverless remove --stage prod
```

---

## 🎯 Configuração Atual

```yaml
Região: us-east-1
S3 Bucket: projeto-vida-prd
Security Group: REDACTED_SECURITY_GROUP_ID
Subnets: 
  - REDACTED_SUBNET_ID_1
  - REDACTED_SUBNET_ID_2
Secrets:
  - projeto-vida/database
  - projeto-vida/cognito
```

---

## 💡 Dicas

1. **Primeira vez**: Use `npm run deploy:prod` (completo)
2. **Atualizações**: Use `npx serverless deploy function -f api --stage prod` (rápido)
3. **Logs**: Mantenha `npm run logs` rodando em outro terminal
4. **Docker**: Certifique-se que está rodando antes do deploy

---

## 📚 Documentação Completa

- **Serverless**: `DEPLOY_SERVERLESS.md`
- **Manual**: `DEPLOY_AWS_LAMBDA.md`
- **Endpoints**: `ENDPOINTS.md`

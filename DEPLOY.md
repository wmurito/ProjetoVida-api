# 🚀 Deploy para AWS Lambda - Produção

## Pré-requisitos

1. **AWS CLI configurado**
```bash
aws configure
# Inserir: Access Key, Secret Key, Region (us-east-1)
```

2. **Serverless Framework instalado**
```bash
npm install -g serverless
```

3. **Dependências Python**
```bash
pip install -r requirements.txt
```

## Passo a Passo

### 1. Criar Secrets no AWS Secrets Manager

```bash
# Banco de dados
aws secretsmanager create-secret \
    --name projeto-vida/database \
    --secret-string '{"username":"<USER>","password":"<PASS>","host":"<HOST>","port":"5432","dbname":"<DB>"}'

# Cognito
aws secretsmanager create-secret \
    --name projeto-vida/cognito \
    --secret-string '{"region":"us-east-1","user_pool_id":"<POOL_ID>","app_client_id":"<CLIENT_ID>"}'
```

### 2. Criar Bucket S3

```bash
aws s3 mb s3://projeto-vida-prd
```

### 3. Configurar params.json

Edite `params.json` com seus valores reais (já existe localmente).

### 4. Deploy

```bash
# Deploy completo
serverless deploy --param-file params.json

# Ou deploy de função específica (mais rápido)
serverless deploy function -f api --param-file params.json
serverless deploy function -f dashboard --param-file params.json
```

## Verificar Deploy

```bash
# Ver informações do deploy
serverless info

# Testar função
serverless invoke -f dashboard

# Ver logs
serverless logs -f api -t
serverless logs -f dashboard -t
```

## Atualizar Código

```bash
# Atualizar apenas código (mais rápido)
serverless deploy function -f api
```

## Remover (cuidado!)

```bash
serverless remove
```

## Troubleshooting

**Erro de permissão:**
- Verificar IAM role tem permissões corretas

**Timeout:**
- Aumentar `timeout` no serverless.yml

**Erro de dependências:**
```bash
npm install serverless-python-requirements
```

## URLs após Deploy

Após deploy, você verá:
```
endpoints:
  ANY - https://xxxxx.execute-api.us-east-1.amazonaws.com/{proxy+}
```

Use essa URL como base da sua API.

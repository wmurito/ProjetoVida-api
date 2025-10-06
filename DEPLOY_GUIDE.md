# Guia de Deploy Seguro para AWS Lambda

Este guia explica como fazer o deploy seguro da aplicação para AWS Lambda usando o Serverless Framework.

## 1. Preparação do Ambiente AWS

### 1.1 Criar segredos no AWS Secrets Manager

```bash
# Criar segredo para as credenciais do banco de dados
aws secretsmanager create-secret \
    --name projeto-vida/database \
    --description "Credenciais do banco de dados do Projeto Vida" \
    --secret-string '{"username":"seu_usuario","password":"sua_senha","host":"seu_host.rds.amazonaws.com","port":"5432","dbname":"seu_banco"}'

# Criar segredo para as configurações do Cognito
aws secretsmanager create-secret \
    --name projeto-vida/cognito \
    --description "Configurações do Cognito para o Projeto Vida" \
    --secret-string '{"region":"us-east-1","user_pool_id":"us-east-1_h48q7uFnQ","app_client_id":"q902jjsdui59k28qk0g3s9o3v"}'
```

### 1.2 Criar um bucket S3 (se ainda não existir)

```bash
# Criar um bucket S3 para armazenar os dados do dashboard
aws s3 mb s3://projeto-vida-prd
```

### 1.3 Configurar VPC (opcional, mas recomendado)

Se seu banco de dados estiver em uma VPC privada, você precisará criar:
- Security Group para o Lambda
- Subnets privadas com acesso ao RDS
- Endpoint VPC para S3 (para evitar custos de NAT Gateway)

## 2. Deploy com Serverless Framework

### 2.1 Instalar dependências

```bash
# Instalar Serverless Framework
npm install -g serverless

# Instalar plugin de requisitos Python
npm install --save-dev serverless-python-requirements
```

### 2.2 Configurar parâmetros para deploy

```bash
# Editar o arquivo params.json com seus valores reais
{
  "s3Bucket": "projeto-vida-prd",
  "s3KeyPrefix": "dashboard_files",
  "dbSecretName": "projeto-vida/database",
  "cognitoSecretName": "projeto-vida/cognito",
  "awsRegion": "us-east-1",
  "securityGroupId": "sg-xxxxxxxxx",
  "subnetId1": "subnet-xxxxxxxxx",
  "subnetId2": "subnet-xxxxxxxxx"
}
```

### 2.3 Fazer o deploy

```bash
# Deploy usando os parâmetros
serverless deploy --param-file params.json
```

## 3. Verificação Pós-Deploy

### 3.1 Testar a função Lambda

```bash
# Invocar a função dashboard manualmente
serverless invoke -f dashboard
```

### 3.2 Verificar logs

```bash
# Ver logs da função dashboard
serverless logs -f dashboard
```

### 3.3 Verificar arquivos no S3

```bash
# Listar arquivos gerados no S3
aws s3 ls s3://projeto-vida-prd/dashboard_files/ --recursive
```

## 4. Manutenção e Atualizações

### 4.1 Atualizar código

Após modificar o código:

```bash
# Atualizar apenas a função dashboard
serverless deploy function -f dashboard
```

### 4.2 Atualizar configurações

Para alterar configurações como agendamento ou memória:

```bash
# Edite serverless.yml e faça o deploy novamente
serverless deploy --param-file params.json
```

## 5. Segurança

### 5.1 Rotação de credenciais

Configure rotação automática de credenciais no AWS Secrets Manager.

### 5.2 Monitoramento

Configure alarmes no CloudWatch para erros nas funções Lambda.

### 5.3 Auditoria

Ative AWS CloudTrail para auditar acessos aos recursos.

## 6. Remoção (se necessário)

```bash
# Remover toda a infraestrutura
serverless remove
```

**IMPORTANTE**: Esta ação remove todas as funções Lambda, mas não remove dados do S3 ou segredos do Secrets Manager.
# 🚀 Guia de Deploy para AWS Lambda

## 📋 Pré-requisitos

### 1. Instalar dependências
```bash
# Node.js e npm
npm install -g serverless

# Python
pip install -r requirements.txt
```

### 2. Configurar AWS CLI
```bash
aws configure
# Insira suas credenciais AWS
```

### 3. Configurar parâmetros
Edite o arquivo `params.json` com suas configurações:
```json
{
  "s3Bucket": "seu-bucket-s3",
  "s3KeyPrefix": "dashboard_files",
  "dbSecretName": "projeto-vida/database",
  "cognitoSecretName": "projeto-vida/cognito",
  "awsRegion": "us-east-1"
}
```

## 🚀 Deploy Rápido

### Windows (PowerShell)
```powershell
.\deploy.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x deploy.sh
./deploy.sh
```

### Deploy Manual
```bash
serverless deploy --config serverless-prod.yml --stage prod
```

## 📁 Arquivos Excluídos do Deploy

O deploy **NÃO inclui** os seguintes arquivos:
- ✅ Documentação (*.md)
- ✅ Arquivos de teste
- ✅ Arquivos de debug
- ✅ Configurações de desenvolvimento
- ✅ Arquivos de cache
- ✅ Logs
- ✅ Arquivos temporários

## 🔧 Configurações de Produção

### Memória e Timeout
- **Memória**: 1024MB
- **Timeout**: 30 segundos
- **Runtime**: Python 3.11

### Otimizações
- ✅ Concorrência provisionada: 2 instâncias
- ✅ Compressão de dependências
- ✅ Exclusão de arquivos desnecessários
- ✅ Configuração otimizada para produção

## 📊 Monitoramento

Após o deploy, monitore:
- CloudWatch Logs
- Métricas de performance
- Erros e exceções
- Uso de memória

## 🔗 Endpoints

Após o deploy, você terá:
- **API Principal**: `https://[seu-dominio]/`
- **Teste**: `https://[seu-dominio]/test`
- **Health Check**: `https://[seu-dominio]/health`

## 🛠️ Troubleshooting

### Erro de permissões
```bash
aws sts get-caller-identity
```

### Erro de dependências
```bash
pip install -r requirements.txt
```

### Erro de configuração
Verifique o arquivo `params.json`

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs no CloudWatch
2. Confirme as configurações AWS
3. Teste localmente primeiro
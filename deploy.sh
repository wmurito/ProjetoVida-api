#!/bin/bash

# 🚀 Script de Deploy para AWS Lambda - Projeto Vida
# Deploy otimizado excluindo arquivos desnecessários

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy da API para AWS Lambda..."
echo "================================================"

# Verificar se o Serverless Framework está instalado
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework não encontrado!"
    echo "📦 Instalando Serverless Framework..."
    npm install -g serverless
fi

# Verificar se as dependências Python estão instaladas
echo "📦 Verificando dependências Python..."
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python -m venv venv
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se o AWS CLI está configurado
echo "🔍 Verificando configuração AWS..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI não configurado!"
    echo "🔧 Configure o AWS CLI com: aws configure"
    exit 1
fi

# Limpar arquivos desnecessários antes do deploy
echo "🧹 Limpando arquivos desnecessários..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -delete
find . -name ".DS_Store" -delete

# Verificar se existe arquivo de parâmetros
if [ ! -f "params.json" ]; then
    echo "⚠️  Arquivo params.json não encontrado!"
    echo "📝 Criando arquivo de parâmetros padrão..."
    cat > params.json << EOF
{
  "s3Bucket": "projeto-vida-prd",
  "s3KeyPrefix": "dashboard_files",
  "dbSecretName": "projeto-vida/database",
  "cognitoSecretName": "projeto-vida/cognito",
  "awsRegion": "us-east-1"
}
EOF
    echo "✅ Arquivo params.json criado com valores padrão"
    echo "🔧 Ajuste os valores conforme necessário antes do deploy"
fi

# Fazer deploy usando o arquivo de produção
echo "🚀 Fazendo deploy para produção..."
serverless deploy --config serverless-prod.yml --stage prod --verbose

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "================================================"
echo "📊 Informações do deploy:"
echo "   • Stage: prod"
echo "   • Runtime: Python 3.11"
echo "   • Memory: 1024MB"
echo "   • Timeout: 30s"
echo "   • Arquivos excluídos: Documentação, testes, debug"
echo ""
echo "🔗 Endpoints disponíveis:"
echo "   • API: https://[seu-dominio]/"
echo "   • Teste: https://[seu-dominio]/test"
echo ""
echo "📋 Próximos passos:"
echo "   1. Testar os endpoints"
echo "   2. Configurar domínio personalizado (opcional)"
echo "   3. Configurar monitoramento"
echo ""
echo "✅ Deploy finalizado!"

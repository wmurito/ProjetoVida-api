#!/bin/bash

# Script para deploy da API com configuração CORS correta
echo "🚀 Fazendo deploy da API com configuração CORS..."

# Verificar se serverless está instalado
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless CLI não encontrado. Instalando..."
    npm install -g serverless
fi

# Verificar se estamos no diretório correto
if [ ! -f "serverless.yml" ]; then
    echo "❌ Arquivo serverless.yml não encontrado. Execute este script no diretório da API."
    exit 1
fi

# Verificar configuração CORS
echo "🔍 Verificando configuração CORS..."
if grep -q "https://master.d1yi28nqqe44f2.amplifyapp.com" serverless.yml; then
    echo "✅ CORS configurado corretamente para o domínio do Amplify"
else
    echo "❌ CORS não configurado para o domínio do Amplify"
    exit 1
fi

# Fazer deploy
echo "🚀 Fazendo deploy da API..."
serverless deploy --stage prod

# Verificar se o deploy foi bem-sucedido
if [ $? -eq 0 ]; then
    echo "✅ Deploy concluído com sucesso!"
    echo "🔗 Testando CORS..."
    
    # Testar CORS
    curl -H "Origin: https://master.d1yi28nqqe44f2.amplifyapp.com" \
         -H "Access-Control-Request-Method: GET" \
         -H "Access-Control-Request-Headers: Content-Type,Authorization" \
         -X OPTIONS \
         https://pteq15e8a6.execute-api.us-east-1.amazonaws.com/
    
    echo ""
    echo "🎉 API deployada com CORS configurado!"
    echo "📋 Próximos passos:"
    echo "   1. Teste a aplicação no Amplify"
    echo "   2. Verifique se os erros de CORS foram resolvidos"
    echo "   3. Monitore os logs da API se necessário"
else
    echo "❌ Erro no deploy. Verifique os logs acima."
    exit 1
fi


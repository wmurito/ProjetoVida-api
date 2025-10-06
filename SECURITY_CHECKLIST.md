# ✅ Checklist de Segurança para Produção

## 🔴 CRÍTICO - Antes do Deploy

### 1. Variáveis de Ambiente
- [ ] Arquivo `.env` está no `.gitignore`
- [ ] Nunca commitar `.env` com credenciais reais
- [ ] Usar AWS Secrets Manager para credenciais em produção
- [ ] Validar que `.env.example` não contém dados sensíveis

### 2. Credenciais AWS
- [ ] Remover qualquer hardcoded AWS credentials
- [ ] Usar IAM Roles para Lambda (não access keys)
- [ ] Rotacionar credenciais regularmente
- [ ] Habilitar MFA para usuários IAM

### 3. Arquivos Sensíveis
- [ ] `params.json` não está commitado (usar `params.example.json`)
- [ ] Nenhum arquivo `.pem`, `.key`, `.crt` no repositório
- [ ] Remover backups de banco de dados do repo
- [ ] Verificar histórico do Git para credenciais expostas

### 4. Banco de Dados
- [ ] Senha do banco em AWS Secrets Manager
- [ ] Conexões SSL/TLS habilitadas
- [ ] Security Groups restringindo acesso
- [ ] Backups automáticos configurados

### 5. S3 Buckets
- [ ] Buckets privados (não públicos)
- [ ] Versionamento habilitado
- [ ] Encryption at rest (AES-256)
- [ ] Bucket policies restritivas
- [ ] CORS configurado corretamente

### 6. API Gateway / Lambda
- [ ] Rate limiting configurado
- [ ] CORS restrito aos domínios necessários
- [ ] Logs habilitados (CloudWatch)
- [ ] Timeout adequado (não muito alto)
- [ ] Memory size otimizado

### 7. Cognito
- [ ] MFA habilitado
- [ ] Políticas de senha fortes
- [ ] Token expiration configurado
- [ ] Refresh token rotation habilitado

## 🟡 IMPORTANTE - Boas Práticas

### 8. Código
- [ ] Validação de input em todos os endpoints
- [ ] Sanitização de dados do usuário
- [ ] Error handling sem expor stack traces
- [ ] Logs sem informações sensíveis

### 9. Dependências
- [ ] Atualizar pacotes com vulnerabilidades conhecidas
- [ ] Usar `pip-audit` ou `safety` para scan
- [ ] Fixar versões no `requirements.txt`

### 10. Monitoramento
- [ ] CloudWatch Alarms configurados
- [ ] Logs centralizados
- [ ] Alertas de erro configurados
- [ ] Métricas de performance

## 🔍 Comandos de Verificação

```bash
# Verificar se há credenciais expostas
git log -p | grep -i "password\|secret\|key\|token"

# Scan de vulnerabilidades
pip install safety
safety check

# Verificar .env não está commitado
git ls-files | grep "\.env$"

# Limpar cache do Git (se necessário)
git rm --cached .env
git rm --cached params.json
```

## 🚨 Em Caso de Exposição de Credenciais

1. **IMEDIATAMENTE** rotacionar todas as credenciais expostas
2. Revogar tokens/keys comprometidos
3. Verificar logs de acesso não autorizado
4. Limpar histórico do Git se necessário:
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch .env" \
   --prune-empty --tag-name-filter cat -- --all
   ```
5. Notificar equipe de segurança

## 📋 Arquivos que NUNCA devem ser commitados

- `.env`
- `params.json`
- `*.pem`, `*.key`, `*.crt`
- `credentials.json`
- `secrets.json`
- Backups de banco (`.sql`, `.dump`)
- Logs com dados sensíveis
- Arquivos de sessão

## ✅ Arquivos OK para commitar

- `.env.example`
- `params.example.json`
- `requirements.txt`
- Código fonte
- Documentação
- Testes (sem dados reais)

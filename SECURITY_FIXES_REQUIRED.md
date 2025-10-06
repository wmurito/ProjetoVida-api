# 🚨 CORREÇÕES DE SEGURANÇA URGENTES

## ⚠️ AÇÃO IMEDIATA NECESSÁRIA

### 1. Arquivo `params.json` está commitado no Git!

**RISCO:** Configurações de produção expostas no repositório.

**SOLUÇÃO:**
```bash
# Remover do Git (mas manter localmente)
git rm --cached params.json

# Commitar a remoção
git commit -m "security: remove params.json from repository"

# Push
git push origin main
```

**IMPORTANTE:** O arquivo `params.json` continuará existindo localmente, mas não será mais rastreado pelo Git.

### 2. Verificar histórico do Git

Se `params.json` ou `.env` já foram commitados antes, o histórico do Git ainda contém essas informações.

**Verificar:**
```bash
git log --all --full-history -- params.json
git log --all --full-history -- .env
```

**Se encontrar commits antigos com dados sensíveis:**
```bash
# CUIDADO: Isso reescreve o histórico!
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch params.json .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (coordenar com equipe)
git push origin --force --all
```

### 3. Rotacionar Credenciais (se expostas)

Se você já fez push de arquivos com credenciais:

1. **AWS:**
   - Rotacionar Access Keys no IAM
   - Atualizar secrets no AWS Secrets Manager
   - Verificar CloudTrail para acessos suspeitos

2. **Banco de Dados:**
   - Alterar senha do RDS
   - Atualizar no Secrets Manager

3. **Cognito:**
   - Rotacionar Client Secret
   - Atualizar configurações

### 4. Configurar .gitignore corretamente

✅ Já foi atualizado! Agora inclui:
- `.env` e variações
- `params.json`
- Certificados e chaves
- Credenciais AWS
- Backups de banco

### 5. Usar params.example.json

✅ Já foi criado! Use como template:
```bash
cp params.example.json params.json
# Editar params.json com valores reais
```

## 📋 Próximos Passos

1. [ ] Executar `git rm --cached params.json`
2. [ ] Verificar histórico do Git
3. [ ] Rotacionar credenciais se necessário
4. [ ] Commitar e fazer push das mudanças
5. [ ] Verificar que `.gitignore` está funcionando:
   ```bash
   git status
   # params.json NÃO deve aparecer como "to be committed"
   ```

## 🔍 Verificação Final

```bash
# Verificar arquivos ignorados
git status --ignored

# Verificar que params.json está ignorado
git check-ignore -v params.json

# Deve retornar algo como:
# .gitignore:XXX:params.json    params.json
```

## 📚 Referências

- [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md) - Checklist completo
- [.gitignore](./.gitignore) - Arquivo atualizado
- [params.example.json](./params.example.json) - Template seguro

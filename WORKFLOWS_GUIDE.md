# 📋 Guia de Workflows GitHub Actions

## Workflows Disponíveis

### 1. **security.yml** - Verificações de Segurança
- **Quando roda:** Push, PR, diariamente às 2h UTC
- **O que faz:**
  - Scan com Bandit
  - Verifica vulnerabilidades (Safety)
  - Detecta secrets
  - CodeQL analysis
  - Docker security scan

### 2. **ci.yml** - Integração Contínua
- **Quando roda:** Push e PR em master/main
- **O que faz:**
  - Instala dependências
  - Roda testes

### 3. **deploy.yml** - Deploy Automático
- **Quando roda:** Push em master ou manual
- **O que faz:**
  - Deploy para AWS Lambda via Serverless
- **Requer:** Secrets AWS configurados

## Como Criar Novo Workflow

### Estrutura Básica

```yaml
name: Nome do Workflow

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  job-name:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Seu passo
      run: echo "Hello World"
```

### Triggers Comuns

```yaml
# Push em branches específicas
on:
  push:
    branches: [ master, develop ]

# Pull requests
on:
  pull_request:
    branches: [ master ]

# Agendamento (cron)
on:
  schedule:
    - cron: '0 2 * * *'  # Diariamente às 2h UTC

# Manual
on:
  workflow_dispatch:

# Múltiplos triggers
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  workflow_dispatch:
```

## Configurar Secrets

1. Vá em: **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret**
3. Adicione:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

## Exemplos de Workflows

### Lint Python
```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: |
        pip install flake8 black
        flake8 .
        black --check .
```

### Build e Test
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: |
        pip install -r requirements.txt
        pytest --cov=. --cov-report=xml
    - uses: codecov/codecov-action@v4
```

### Deploy Condicional
```yaml
name: Deploy

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    steps:
    - uses: actions/checkout@v4
    - name: Deploy
      run: echo "Deploying..."
```

## Comandos Úteis

```bash
# Criar novo workflow
mkdir -p .github/workflows
touch .github/workflows/novo-workflow.yml

# Validar sintaxe (localmente com act)
act -l

# Ver workflows no GitHub
# Settings → Actions → General
```

## Boas Práticas

1. **Use versões fixas** de actions (v4, não @latest)
2. **Minimize secrets** - use IAM roles quando possível
3. **Cache dependências** para builds mais rápidos
4. **Fail fast** - pare em erros críticos
5. **Nomeie steps claramente**
6. **Use matrix** para testar múltiplas versões

## Troubleshooting

- **Workflow não roda:** Verifique triggers e branches
- **Secrets não funcionam:** Verifique nomes exatos
- **Timeout:** Aumente com `timeout-minutes: 30`
- **Permissões:** Configure em `permissions:`

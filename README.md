# ProjetoVida — Backend (API)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi) ![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws)

API RESTful do sistema de gerenciamento de dados clínicos e acompanhamento de pacientes oncológicos do **Projeto Vida**.

---

## Sobre

Backend serverless em FastAPI com endpoints para:

- **Pacientes** — CRUD completo com dados clínicos e histórico
- **Dashboard** — Métricas calculadas server-side (sobrevida, recidiva, delta-T, SUS)
- **Exportação** — Geração de planilhas Excel via Pandas/Openpyxl
- **Upload seguro** — Upload de documentos com sanitização contra injeções
- **Autenticação** — Validação de JWT via AWS Cognito

---

## Stack

| Tecnologia | Uso |
|---|---|
| FastAPI + Uvicorn | Framework e servidor ASGI |
| Mangum | Adaptador para AWS Lambda |
| SQLAlchemy v2 | ORM |
| PostgreSQL | Banco de dados de produção |
| SQLite | Banco de dados local (desenvolvimento) |
| Pydantic | Validação de schemas |
| Boto3 | AWS SDK (S3, Secrets Manager) |
| Pandas + Openpyxl | Exportação para Excel |
| Slowapi | Rate limiting |
| python-jose + passlib | Criptografia e JWT |
| Serverless Framework | Deploy na AWS Lambda |

---

## Configuração Local

### 1. Criar ambiente virtual e instalar dependências

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com os valores reais:

```bash
cp env_example.txt .env
```

Edite o `.env`:

```env
DATABASE_URL=postgresql://postgres:senha@localhost:5432/projetovida
DB_SECRET_NAME=projeto-vida/database
JWT_SECRET_KEY=<CHAVE_GERADA_ALEATORIAMENTE>
CSRF_SECRET_KEY=<CHAVE_GERADA_ALEATORIAMENTE>
ALLOWED_ORIGINS=http://localhost:5173
```

> ⚠️ Nunca commite o arquivo `.env` com valores reais.

### 3. Rodar em desenvolvimento

```bash
uvicorn main:app --reload --port 8000
```

Acesse: `http://localhost:8000/docs`

---

## Deploy (AWS Lambda + Serverless Framework)

```bash
# Instalar Serverless Framework
npm install -g serverless

# Configurar os parâmetros SSM no AWS antes do deploy
aws ssm put-parameter --name "/projeto-vida/vpc/security-group-id" --value "<ID>" --type SecureString --region us-east-1
aws ssm put-parameter --name "/projeto-vida/vpc/subnet-id-1" --value "<ID>" --type SecureString --region us-east-1
aws ssm put-parameter --name "/projeto-vida/vpc/subnet-id-2" --value "<ID>" --type SecureString --region us-east-1

# Deploy
serverless deploy --stage prod
```

As credenciais do banco e Cognito são obtidas automaticamente via **AWS Secrets Manager** em produção.

---

## Segurança

- Autenticação JWT via AWS Cognito (verificação de assinatura)
- Rate limiting por IP (Slowapi)
- Validação de schemas com Pydantic
- IDs de infraestrutura AWS no SSM Parameter Store
- Credenciais de banco no AWS Secrets Manager
- Logs sanitizados (sem dados sensíveis)
- CORS configurado por lista de origens permitidas

---

## Estrutura

```
ProjetoVida-api/
├── main.py              # Entrypoint + rotas principais
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── crud.py              # Operações de banco de dados
├── dashboard.py         # Endpoints e lógica do dashboard
├── auth.py              # Autenticação e JWT
├── database.py          # Conexão com banco (prod/dev)
├── security.py          # Middlewares de segurança
├── exportar.py          # Exportação para Excel
├── s3_service.py        # Integração com S3
├── encryption.py        # Utilitários de criptografia
└── serverless.yml       # Configuração de deploy AWS Lambda
```

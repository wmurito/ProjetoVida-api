# ProjetoVida API

API backend para o sistema ProjetoVida, desenvolvida com FastAPI e AWS Lambda.

## Tecnologias

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **AWS Lambda** - Serverless
- **AWS Cognito** - Autenticação
- **AWS S3** - Armazenamento

## Estrutura

```
├── main.py              # API principal
├── auth.py              # Autenticação
├── models.py            # Modelos do banco
├── schemas.py           # Schemas Pydantic
├── crud.py              # Operações CRUD
├── database.py          # Configuração do banco
├── s3_service.py        # Serviços S3
├── lambda_dashboard.py  # Lambda dashboard
└── serverless.yml       # Configuração deploy
```

## Deploy

```bash
# Instalar dependências
npm install

# Deploy para AWS
serverless deploy
```

## Desenvolvimento Local

```bash
# Ativar ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python main.py
```

## Documentação

- API: http://localhost:8000/docs
- Deploy: Consulte documentação interna

## Licença

Proprietary - Todos os direitos reservados

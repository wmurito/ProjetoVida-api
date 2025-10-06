# Projeto Vida - Dashboard de Dados Oncológicos

API e dashboard para gerenciamento de dados de pacientes oncológicos.

## Estrutura do Projeto

- `main.py`: API FastAPI principal
- `lambda_dashboard.py`: Gerador de dashboard para AWS Lambda
- `models.py`: Modelos SQLAlchemy
- `schemas.py`: Schemas Pydantic
- `crud.py`: Operações CRUD
- `auth.py`: Autenticação e autorização
- `database.py`: Configuração do banco de dados

## Configuração

1. Crie um arquivo `.env` baseado no `.env.example`
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute localmente: `uvicorn main:app --reload`

## Implantação no AWS Lambda

```bash
# Instalar o Serverless Framework
npm install -g serverless

# Configurar credenciais AWS
aws configure

# Implantar
serverless deploy
```

## Segurança

- As credenciais AWS são gerenciadas por IAM roles
- O banco de dados é acessado através de uma VPC
- Autenticação via tokens JWT

## Custos Estimados

Para 50 pacientes mensais:
- AWS Lambda: < $0.20/mês
- AWS S3: < $0.01/mês
- RDS PostgreSQL: ~$15-30/mês

Total estimado: ~$15-30/mês
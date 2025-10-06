# ProjetoVida API

## Como rodar o backend

### 1. Ativar ambiente virtual

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Edite o arquivo `.env` com suas credenciais reais.

### 4. Rodar o servidor

```bash
# Desenvolvimento (com reload automático)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou simplesmente
python main.py
```

### 5. Acessar a API

- API: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

## Comandos úteis

```bash
# Instalar nova dependência
pip install nome-pacote
pip freeze > requirements.txt

# Verificar se está rodando
curl http://localhost:8000
```

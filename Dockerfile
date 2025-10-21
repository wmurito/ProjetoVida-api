FROM public.ecr.aws/lambda/python:3.11

# Copiar requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY *.py ${LAMBDA_TASK_ROOT}/

# Comando handler
CMD ["main.handler"]

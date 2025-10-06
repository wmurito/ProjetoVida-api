import json
import os
import boto3
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from botocore.exceptions import ClientError

# Configurar logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configurações
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_KEY_PREFIX = os.environ.get('S3_KEY_PREFIX')
DB_SECRET_NAME = os.environ.get('DB_SECRET_NAME', 'projeto-vida/database')

# AWS Clients
s3_client = boto3.client('s3')
secretsmanager_client = boto3.client('secretsmanager')

def get_db_connection_string():
    """Recupera a string de conexão do banco de dados do AWS Secrets Manager"""
    try:
        logger.info(f"Recuperando segredo do banco de dados: {DB_SECRET_NAME}")
        response = secretsmanager_client.get_secret_value(SecretId=DB_SECRET_NAME)
        secret = json.loads(response['SecretString'])
        
        # Formato esperado do segredo: {"host": "...", "port": "...", "dbname": "...", "username": "...", "password": "..."}
        conn_string = f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}"
        return conn_string
    except ClientError as e:
        logger.error(f"Erro ao recuperar segredo do banco de dados: {str(e)}")
        # Fallback para variável de ambiente se configurada
        if os.environ.get('DATABASE_URL'):
            logger.warning("Usando DATABASE_URL da variável de ambiente como fallback")
            return os.environ.get('DATABASE_URL')
        raise

def get_db_engine():
    """Cria uma nova conexão com o banco de dados"""
    logger.info("Conectando ao banco de dados...")
    db_url = get_db_connection_string()
    return create_engine(db_url)

def salvar_json_no_s3(bucket_name, s3_key_path, data_content):
    """Salva conteúdo como um arquivo JSON no S3."""
    full_s3_path = f"s3://{bucket_name}/{s3_key_path}"
    logger.info(f"Enviando para S3 → {full_s3_path}")
    try:
        body_data = data_content
        if not isinstance(data_content, (dict, list)):
            file_key_name = os.path.splitext(os.path.basename(s3_key_path))[0]
            body_data = {file_key_name: data_content}

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key_path,
            Body=json.dumps(body_data, indent=2, default=str),
            ContentType='application/json'
        )
        logger.info(f"Arquivo {s3_key_path} salvo com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar {s3_key_path} no S3: {str(e)}")
        return False

# --- Funções para gerar dados dos GRÁFICOS ---
def gerar_e_salvar_estadiamento(engine, bucket, prefix):
    logger.info("Gerando dados de Estadiamento...")
    try:
        data = pd.read_sql("""
            SELECT COALESCE(estagio_clinico_pre_qxt, 'Não informado') AS estagio, COUNT(*) AS quantidade
            FROM masto.tratamento GROUP BY estagio_clinico_pre_qxt ORDER BY quantidade DESC;
        """, engine).to_dict(orient='records')
        return salvar_json_no_s3(bucket, f"{prefix}/graficos/estadiamento.json", data)
    except Exception as e:
        logger.error(f"Erro ao gerar dados de estadiamento: {str(e)}")
        return False

def gerar_e_salvar_sobrevida(engine, bucket, prefix):
    logger.info("Gerando dados de Sobrevida Global...")
    try:
        data = pd.read_sql("""
            SELECT CASE WHEN morte IS TRUE THEN 'Óbito' ELSE 'Vivo' END AS status, COUNT(*) AS quantidade
            FROM masto.desfecho GROUP BY status;
        """, engine).to_dict(orient='records')
        return salvar_json_no_s3(bucket, f"{prefix}/graficos/sobrevida.json", data)
    except Exception as e:
        logger.error(f"Erro ao gerar dados de sobrevida: {str(e)}")
        return False

def gerar_e_salvar_recidiva(engine, bucket, prefix):
    logger.info("Gerando dados de Taxa de Recidiva...")
    try:
        data = pd.read_sql("""
            SELECT 'Recidiva Local' AS tipo, COUNT(*) AS quantidade FROM masto.desfecho WHERE recidiva_local IS TRUE
            UNION ALL
            SELECT 'Recidiva Regional' AS tipo, COUNT(*) AS quantidade FROM masto.desfecho WHERE recidiva_regional IS TRUE
            UNION ALL
            SELECT 'Metástase' AS tipo, COUNT(*) AS quantidade FROM masto.desfecho WHERE metastase IS TRUE;
        """, engine).to_dict(orient='records')
        return salvar_json_no_s3(bucket, f"{prefix}/graficos/recidiva.json", data)
    except Exception as e:
        logger.error(f"Erro ao gerar dados de recidiva: {str(e)}")
        return False

def gerar_e_salvar_delta_t(engine, bucket, prefix):
    logger.info("Gerando dados de Média dos Tempos (Delta T)...")
    try:
        delta_t_query = """
            SELECT 'Diagnóstico → Cirurgia' AS processo, AVG(EXTRACT(EPOCH FROM (data_cirurgia::TIMESTAMP - data_core_biopsy::TIMESTAMP))/86400) AS media_dias
            FROM masto.tempos_diagnostico WHERE data_cirurgia IS NOT NULL AND data_core_biopsy IS NOT NULL UNION ALL
            SELECT 'Diagnóstico → Início QT' AS processo, AVG(EXTRACT(EPOCH FROM (inicio_quimioterapia::TIMESTAMP - data_core_biopsy::TIMESTAMP))/86400) AS media_dias
            FROM masto.tratamento JOIN masto.tempos_diagnostico USING (paciente_id) WHERE inicio_quimioterapia IS NOT NULL AND data_core_biopsy IS NOT NULL UNION ALL
            SELECT 'Diagnóstico → Radioterapia' AS processo, AVG(EXTRACT(EPOCH FROM (inicio_radioterapia::TIMESTAMP - data_core_biopsy::TIMESTAMP))/86400) AS media_dias
            FROM masto.tratamento JOIN masto.tempos_diagnostico USING (paciente_id) WHERE inicio_radioterapia IS NOT NULL AND data_core_biopsy IS NOT NULL;
        """
        delta_t_data = pd.read_sql(delta_t_query, engine).to_dict(orient='records')
        processed_data = [{**r, "media_dias": round(r['media_dias'], 1) if r.get('media_dias') is not None else None} for r in delta_t_data]
        return salvar_json_no_s3(bucket, f"{prefix}/graficos/delta_t.json", processed_data)
    except Exception as e:
        logger.error(f"Erro ao gerar dados de delta_t: {str(e)}")
        return False

# --- Funções para gerar dados dos KPIs (CARDS) ---
def gerar_e_salvar_kpi_total_pacientes(engine, bucket, prefix):
    logger.info("Gerando KPI: Total de Pacientes...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM masto.paciente;"))
            valor = result.scalar_one_or_none() or 0
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/total_pacientes.json", {"total_casos": valor})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI total_pacientes: {str(e)}")
        return False

def gerar_e_salvar_kpi_total_obitos(engine, bucket, prefix):
    logger.info("Gerando KPI: Total de Óbitos...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM masto.desfecho WHERE morte = TRUE;"))
            valor = result.scalar_one_or_none() or 0
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/total_obitos.json", {"total_obitos": valor})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI total_obitos: {str(e)}")
        return False

def gerar_e_salvar_kpi_taxa_mortalidade(engine, bucket, prefix):
    logger.info("Gerando KPI: Taxa de Mortalidade...")
    try:
        with engine.connect() as connection:
            total_pacientes_res = connection.execute(text("SELECT COUNT(*) FROM masto.paciente;")).scalar_one_or_none()
            total_obitos_res = connection.execute(text("SELECT COUNT(*) FROM masto.desfecho WHERE morte = TRUE;")).scalar_one_or_none()
            total_pacientes = total_pacientes_res or 0
            total_obitos = total_obitos_res or 0
            taxa = (total_obitos / total_pacientes) * 100 if total_pacientes > 0 else 0
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/taxa_mortalidade.json", {"taxa_mortalidade": round(taxa, 1)})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI taxa_mortalidade: {str(e)}")
        return False

def gerar_e_salvar_kpi_idade_media_diagnostico(engine, bucket, prefix):
    logger.info("Gerando KPI: Idade Média no Diagnóstico...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT AVG(idade_diagnostico) FROM masto.historia_doenca_atual WHERE idade_diagnostico IS NOT NULL;"))
            valor = result.scalar_one_or_none()
            valor_float = round(float(valor or 0), 0)
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/idade_media_diagnostico.json", {"idade_media": valor_float})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI idade_media_diagnostico: {str(e)}")
        return False

def gerar_e_salvar_kpi_tamanho_medio_tumor(engine, bucket, prefix):
    logger.info("Gerando KPI: Tamanho Médio do Tumor...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT AVG(tamanho_tumoral) FROM masto.histologia WHERE tamanho_tumoral IS NOT NULL;"))
            valor = result.scalar_one_or_none()
            valor_float = round(float(valor or 0), 1)
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/tamanho_medio_tumor.json", {"tamanho_medio_cm": valor_float})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI tamanho_medio_tumor: {str(e)}")
        return False

def gerar_e_salvar_kpi_media_risco_gail(engine, bucket, prefix):
    logger.info("Gerando KPI: Média Risco Gail...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT AVG(score_gail) FROM masto.historia_doenca_atual WHERE score_gail IS NOT NULL;"))
            valor = result.scalar_one_or_none()
            valor_float = round(float(valor or 0), 2)
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/media_risco_gail.json", {"media_risco_5_anos": valor_float})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI media_risco_gail: {str(e)}")
        return False

def gerar_e_salvar_kpi_media_risco_tyrer(engine, bucket, prefix):
    logger.info("Gerando KPI: Média Risco Tyrer-Cuzick...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT AVG(score_tyrer_cuzick) FROM masto.historia_doenca_atual WHERE score_tyrer_cuzick IS NOT NULL;"))
            valor = result.scalar_one_or_none()
            valor_float = round(float(valor or 0), 2)
        return salvar_json_no_s3(bucket, f"{prefix}/kpis/media_risco_tyrer_cuzick.json", {"media_risco_10_anos": valor_float})
    except Exception as e:
        logger.error(f"Erro ao gerar KPI media_risco_tyrer: {str(e)}")
        return False

def gerar_todos_dados_dashboard():
    """Gera todos os dados do dashboard e salva no S3"""
    # Validar configurações
    if not S3_BUCKET or not S3_KEY_PREFIX:
        logger.error("ERRO: S3_BUCKET ou S3_KEY_PREFIX não configurados. Arquivos não serão enviados ao S3.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Configurações S3 ausentes"})
        }
    
    try:
        # Criar conexão com o banco de dados
        engine = get_db_engine()
        
        # Gerar todos os dados
        resultados = {}
        
        # Gráficos
        resultados["estadiamento"] = gerar_e_salvar_estadiamento(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["sobrevida"] = gerar_e_salvar_sobrevida(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["recidiva"] = gerar_e_salvar_recidiva(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["delta_t"] = gerar_e_salvar_delta_t(engine, S3_BUCKET, S3_KEY_PREFIX)
        
        # KPIs
        resultados["total_pacientes"] = gerar_e_salvar_kpi_total_pacientes(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["total_obitos"] = gerar_e_salvar_kpi_total_obitos(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["taxa_mortalidade"] = gerar_e_salvar_kpi_taxa_mortalidade(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["idade_media"] = gerar_e_salvar_kpi_idade_media_diagnostico(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["tamanho_tumor"] = gerar_e_salvar_kpi_tamanho_medio_tumor(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["risco_gail"] = gerar_e_salvar_kpi_media_risco_gail(engine, S3_BUCKET, S3_KEY_PREFIX)
        resultados["risco_tyrer"] = gerar_e_salvar_kpi_media_risco_tyrer(engine, S3_BUCKET, S3_KEY_PREFIX)
        
        # Verificar se todos os dados foram gerados com sucesso
        todos_ok = all(resultados.values())
        
        # Fechar conexão com o banco de dados
        engine.dispose()
        
        if todos_ok:
            logger.info("Todos os dados do dashboard foram gerados e salvos com sucesso!")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Dashboard gerado com sucesso"})
            }
        else:
            logger.warning("Alguns dados do dashboard não puderam ser gerados.")
            return {
                "statusCode": 207,  # Multi-Status
                "body": json.dumps({"message": "Dashboard gerado parcialmente", "detalhes": resultados})
            }
            
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Falha ao gerar dashboard: {str(e)}"})
        }

def lambda_handler(event, context):
    """Função handler para AWS Lambda"""
    logger.info("Iniciando geração do dashboard...")
    return gerar_todos_dados_dashboard()

# Para execução local
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
    
    # Configuração para teste local
    os.environ['S3_BUCKET'] = os.environ.get('S3_BUCKET', 'projeto-vida-prd')
    os.environ['S3_KEY_PREFIX'] = os.environ.get('S3_KEY_PREFIX', 'dashboard_files')
    
    resultado = gerar_todos_dados_dashboard()
    print(json.dumps(resultado, indent=2))
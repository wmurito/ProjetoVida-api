# exportar.py
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import datetime
import io

# Carrega variáveis de ambiente (para DB_URL)
load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

def gerar_relatorio_pacientes_excel():
    """
    Busca todos os dados dos pacientes, junta as tabelas e gera um arquivo Excel.
    Retorna o caminho do arquivo gerado ou None em caso de erro.
    """
    if not DB_URL:
        print("ERRO: Variável de ambiente DB_URL não definida.")
        return None

    print("🔗 Conectando ao banco de dados para exportação...")
    try:
        engine = create_engine(DB_URL)
    except Exception as e:
        print(f"Erro ao criar engine do banco de dados: {e}")
        return None

    query = """
    SELECT 
        p.paciente_id AS "ID Paciente (Paciente)", 
        p.nome_completo AS "Nome Completo (Paciente)",
        p.idade AS "Idade (Paciente)",
        p.endereco AS "Endereço (Paciente)",
        p.cidade AS "Cidade (Paciente)",
        p.data_nascimento AS "Data Nascimento (Paciente)",
        p.telefone AS "Telefone (Paciente)",
        p.naturalidade AS "Naturalidade (Paciente)",
        p.altura AS "Altura (Paciente)",
        p.peso AS "Peso (Paciente)",
        p.imc AS "IMC (Paciente)",
        p.cor_etnia AS "Cor/Etnia (Paciente)",
        p.escolaridade AS "Escolaridade (Paciente)",
        p.renda_familiar AS "Renda Familiar (Paciente)",

        hp.id AS "ID (Hist. Patológica)",
        hp.hipertensao AS "Hipertensão (Hist. Patológica)",
        hp.hipotireoidismo AS "Hipotireoidismo (Hist. Patológica)",
        hp.ansiedade AS "Ansiedade (Hist. Patológica)",
        hp.depressao AS "Depressão (Hist. Patológica)",
        hp.diabetes AS "Diabetes (Hist. Patológica)",
        hp.outros AS "Outros (Hist. Patológica)",

        hf.id AS "ID (Hist. Familiar)",
        hf.cancer_mama AS "Câncer Mama (Hist. Familiar)",
        hf.parentesco_mama AS "Parentesco Câncer Mama (Hist. Familiar)",
        hf.idade_diagnostico_mama AS "Idade Diag. Câncer Mama (Hist. Familiar)",
        hf.cancer_ovario AS "Câncer Ovário (Hist. Familiar)",
        hf.parentesco_ovario AS "Parentesco Câncer Ovário (Hist. Familiar)",
        hf.idade_diagnostico_ovario AS "Idade Diag. Câncer Ovário (Hist. Familiar)",
        hf.outros AS "Outros (Hist. Familiar)",

        hv.id AS "ID (Hábitos de Vida)",
        hv.tabagismo_carga AS "Carga Tabágica (Hábitos de Vida)",
        hv.tabagismo_tempo_anos AS "Tempo Tabagismo (anos) (Hábitos de Vida)",
        hv.etilismo_dose_diaria AS "Dose Diária Etilismo (Hábitos de Vida)",
        hv.etilismo_tempo_anos AS "Tempo Etilismo (anos) (Hábitos de Vida)",

        pa.id AS "ID (Paridade)",
        pa.gesta AS "Gesta (Paridade)",
        pa.para AS "Para (Paridade)",
        pa.aborto AS "Aborto (Paridade)",
        pa.idade_primeiro_filho AS "Idade Primeiro Filho (Paridade)",
        pa.amamentou AS "Amamentou (Paridade)",
        pa.tempo_amamentacao_meses AS "Tempo Amamentação (meses) (Paridade)",
        pa.menarca_idade AS "Idade Menarca (Paridade)",
        pa.menopausa AS "Menopausa (Paridade)",
        pa.idade_menopausa AS "Idade Menopausa (Paridade)",
        pa.trh_uso AS "Uso TRH (Paridade)",
        pa.tempo_uso_trh AS "Tempo Uso TRH (Paridade)",
        pa.tipo_terapia AS "Tipo Terapia TRH (Paridade)",

        hda.id AS "ID (Hist. Doença Atual)",
        hda.idade_diagnostico AS "Idade Diagnóstico (Hist. Doença Atual)",
        hda.score_tyrer_cuzick AS "Score Tyrer-Cuzick (Hist. Doença Atual)",
        hda.score_canrisk AS "Score CanRisk (Hist. Doença Atual)",
        hda.score_gail AS "Score Gail (Hist. Doença Atual)",

        hi.id AS "ID (Histologia)",
        hi.subtipo_core_re AS "Subtipo Core RE (Histologia)",
        hi.subtipo_core_rp AS "Subtipo Core RP (Histologia)",
        hi.subtipo_core_her2 AS "Subtipo Core HER2 (Histologia)",
        hi.subtipo_core_ki67 AS "Subtipo Core Ki67 (Histologia)",
        hi.subtipo_cirurgia_re AS "Subtipo Cirurgia RE (Histologia)",
        hi.subtipo_cirurgia_rp AS "Subtipo Cirurgia RP (Histologia)",
        hi.subtipo_cirurgia_her2 AS "Subtipo Cirurgia HER2 (Histologia)",
        hi.subtipo_cirurgia_ki67 AS "Subtipo Cirurgia Ki67 (Histologia)",
        hi.tamanho_tumoral AS "Tamanho Tumoral (cm) (Histologia)",
        hi.grau_tumoral_cirurgia AS "Grau Tumoral Cirurgia (Histologia)",
        hi.margens_comprometidas AS "Margens Comprometidas (Histologia)",
        hi.margens_local AS "Local Margens Comprometidas (Histologia)",
        hi.biopsia_linfonodo_sentinela AS "Biópsia Linfonodo Sentinela (Histologia)",
        hi.bls_numerador AS "BLS Numerador (Histologia)",
        hi.bls_denominador AS "BLS Denominador (Histologia)",
        hi.linfadenectomia_axilar AS "Linfadenectomia Axilar (Histologia)",
        hi.ea_numerador AS "EA Numerador (Histologia)",
        hi.ea_denominador AS "EA Denominador (Histologia)",

        t.id AS "ID (Tratamento)",
        t.tratamento_neoadjuvante AS "Tratamento Neoadjuvante (Tratamento)",
        t.inicio_neoadjuvante AS "Início Neoadjuvante (Tratamento)",
        t.termino_neoadjuvante AS "Término Neoadjuvante (Tratamento)",
        t.qual_neoadjuvante AS "Qual Neoadjuvante (Tratamento)",
        t.estagio_clinico_pre_qxt AS "Estágio Clínico Pré-QXT (Tratamento)",
        t.imunoterapia AS "Imunoterapia (Tratamento)",
        t.adjuvancia AS "Adjuvância (Tratamento)",
        t.quimioterapia AS "Quimioterapia (Tratamento)",
        t.inicio_quimioterapia AS "Início Quimioterapia (Tratamento)",
        t.fim_quimioterapia AS "Fim Quimioterapia (Tratamento)",
        t.radioterapia_tipo AS "Tipo Radioterapia (Tratamento)",
        t.radioterapia_sessoes AS "Sessões Radioterapia (Tratamento)",
        t.inicio_radioterapia AS "Início Radioterapia (Tratamento)",
        t.fim_radioterapia AS "Fim Radioterapia (Tratamento)",
        t.endocrinoterapia AS "Endocrinoterapia (Tratamento)",
        t.inicio_endocrino AS "Início Endocrinoterapia (Tratamento)",
        t.fim_endocrino AS "Fim Endocrinoterapia (Tratamento)",
        t.terapia_alvo AS "Terapia Alvo (Tratamento)",
        t.inicio_terapia_alvo AS "Início Terapia Alvo (Tratamento)",
        t.fim_terapia_alvo AS "Fim Terapia Alvo (Tratamento)",

        d.id AS "ID (Desfecho)",
        d.morte AS "Morte (Desfecho)",
        d.data_morte AS "Data Morte (Desfecho)",
        d.causa_morte AS "Causa Morte (Desfecho)",
        d.metastase AS "Metástase (Desfecho)",
        d.data_metastase AS "Data Metástase (Desfecho)",
        d.local_metastase AS "Local Metástase (Desfecho)",
        d.recidiva_local AS "Recidiva Local (Desfecho)",
        d.data_recidiva_local AS "Data Recidiva Local (Desfecho)",
        d.recidiva_regional AS "Recidiva Regional (Desfecho)",
        d.data_recidiva_regional AS "Data Recidiva Regional (Desfecho)",
        d.sitio_recidiva_regional AS "Sítio Recidiva Regional (Desfecho)",

        td.id AS "ID (Tempos Diag.)",
        td.data_mamografia AS "Data Mamografia (Tempos Diag.)",
        td.data_usg AS "Data USG (Tempos Diag.)",
        td.data_rm AS "Data RM (Tempos Diag.)",
        td.data_primeira_consulta AS "Data Primeira Consulta (Tempos Diag.)",
        td.data_core_biopsy AS "Data Core Biopsy (Tempos Diag.)",
        td.data_cirurgia AS "Data Cirurgia (Tempos Diag.)"
    FROM 
        masto.paciente p
    LEFT JOIN masto.historia_patologica hp ON hp.paciente_id = p.paciente_id
    LEFT JOIN masto.historia_familiar hf ON hf.paciente_id = p.paciente_id
    LEFT JOIN masto.habitos_de_vida hv ON hv.paciente_id = p.paciente_id
    LEFT JOIN masto.paridade pa ON pa.paciente_id = p.paciente_id
    LEFT JOIN masto.historia_doenca_atual hda ON hda.paciente_id = p.paciente_id
    LEFT JOIN masto.histologia hi ON hi.paciente_id = p.paciente_id
    LEFT JOIN masto.tratamento t ON t.paciente_id = p.paciente_id
    LEFT JOIN masto.desfecho d ON d.paciente_id = p.paciente_id
    LEFT JOIN masto.tempos_diagnostico td ON td.paciente_id = p.paciente_id
    ORDER BY p.paciente_id;
    """
    
    print("🔄 Executando a query para buscar dados completos dos pacientes...")
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(query, connection)
    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        return None
    
    if df.empty:
        print("ℹ️ Nenhum dado encontrado para exportar.")
        return None

    print("💾 Gerando arquivo Excel em memória...")
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        excel_data = output.getvalue()
        output.close()
        print(f"✅ Arquivo Excel gerado com sucesso em memória.")
        return excel_data
    except Exception as e:
        print(f"Erro ao gerar o arquivo Excel na memória: {e}")
        return None

if __name__ == '__main__':
    # Este bloco é para teste local do script
    print("--- Iniciando Teste de Exportação ---")
    bytes_data = gerar_relatorio_pacientes_excel()
    if bytes_data:
        print(f"Sucesso! Buffer gerado com {len(bytes_data)} bytes.")
    else:
        print("Falha ao gerar o buffer em memória.")
    print("--- Teste de Exportação Concluído ---")
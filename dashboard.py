from sqlalchemy.orm import Session


# ✅ Distribuição por Estadiamento no Diagnóstico
def get_estadiamento(db: Session):
    result = db.execute("""
        SELECT 
            COALESCE(estadiamento_clinico, 'Não informado') AS estagio, 
            COUNT(*) AS total
        FROM masto.historia_doenca
        GROUP BY estadiamento_clinico
        ORDER BY total DESC
    """).fetchall()

    return [{"estagio": r[0], "total": r[1]} for r in result]


# ✅ Sobrevida Global (Vivo x Óbito)
def get_sobrevida_global(db: Session):
    result = db.execute("""
        SELECT 
            COALESCE(status_vital, 'Não informado') AS status, 
            COUNT(*) AS total
        FROM masto.desfecho
        GROUP BY status_vital
    """).fetchall()

    return [{"status": r[0], "total": r[1]} for r in result]


# ✅ Taxa de Recidiva (Local, Regional, Metástase)
def get_taxa_recidiva(db: Session):
    result = db.execute("""
        SELECT tipo, COUNT(*) AS total
        FROM (
            SELECT 'Recidiva Local' AS tipo FROM masto.desfecho WHERE recidiva_local IS TRUE
            UNION ALL
            SELECT 'Recidiva Regional' FROM masto.desfecho WHERE recidiva_regional IS TRUE
            UNION ALL
            SELECT 'Metástase' FROM masto.desfecho WHERE metastases IS NOT NULL AND metastases::text != '[]'
        ) AS eventos
        GROUP BY tipo
    """).fetchall()

    return [{"tipo": r[0], "total": r[1]} for r in result]


# ✅ Média dos Tempos (Delta T) — entre diagnóstico, cirurgia, QT e RT
def get_media_delta_t(db: Session):
    result = db.execute("""
        SELECT 
            'Diagnóstico → Cirurgia' AS processo, 
            AVG(DATE_PART('day', td.data_cirurgia - td.data_diagnostico)) AS media_dias
        FROM masto.tempos_diagnostico td
        WHERE td.data_cirurgia IS NOT NULL AND td.data_diagnostico IS NOT NULL

        UNION ALL

        SELECT 
            'Diagnóstico → Início Tratamento', 
            AVG(DATE_PART('day', td.data_inicio_tratamento - td.data_diagnostico)) 
        FROM masto.tempos_diagnostico td
        WHERE td.data_inicio_tratamento IS NOT NULL AND td.data_diagnostico IS NOT NULL

        UNION ALL

        SELECT 
            'Primeira Consulta → Diagnóstico', 
            AVG(DATE_PART('day', td.data_diagnostico - td.data_primeira_consulta)) 
        FROM masto.tempos_diagnostico td
        WHERE td.data_diagnostico IS NOT NULL AND td.data_primeira_consulta IS NOT NULL
    """).fetchall()

    return [
        {"processo": r[0], "media_dias": round(r[1], 1) if r[1] else None}
        for r in result
    ]

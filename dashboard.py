from sqlalchemy.orm import Session


# ✅ Distribuição por Estadiamento no Diagnóstico
def get_estadiamento(db: Session):
    result = db.execute("""
        SELECT 
            COALESCE(estagio_clinico_pre_qxt, 'Não informado') AS estagio, 
            COUNT(*) AS total
        FROM masto.tratamento
        GROUP BY estagio_clinico_pre_qxt
        ORDER BY total DESC
    """).fetchall()

    return [{"estagio": r[0], "total": r[1]} for r in result]


# ✅ Sobrevida Global (Vivo x Óbito)
def get_sobrevida_global(db: Session):
    result = db.execute("""
        SELECT 
            CASE WHEN morte IS TRUE THEN 'Óbito' ELSE 'Vivo' END AS status, 
            COUNT(*) AS total
        FROM masto.desfecho
        GROUP BY status
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
            SELECT 'Metástase' FROM masto.desfecho WHERE metastase IS TRUE
        ) AS eventos
        GROUP BY tipo
    """).fetchall()

    return [{"tipo": r[0], "total": r[1]} for r in result]


# ✅ Média dos Tempos (Delta T) — entre diagnóstico, cirurgia, QT e RT
def get_media_delta_t(db: Session):
    result = db.execute("""
        SELECT 
            'Diagnóstico → Cirurgia' AS processo, 
            AVG(DATE_PART('day', data_cirurgia - inicio_neoadjuvante)) AS media_dias
        FROM masto.tratamento
        WHERE data_cirurgia IS NOT NULL AND inicio_neoadjuvante IS NOT NULL

        UNION ALL

        SELECT 
            'Diagnóstico → Início QT', 
            AVG(DATE_PART('day', inicio_quimioterapia - inicio_neoadjuvante)) 
        FROM masto.tratamento
        WHERE inicio_quimioterapia IS NOT NULL AND inicio_neoadjuvante IS NOT NULL

        UNION ALL

        SELECT 
            'Diagnóstico → Início RT', 
            AVG(DATE_PART('day', inicio_radioterapia - inicio_neoadjuvante)) 
        FROM masto.tratamento
        WHERE inicio_radioterapia IS NOT NULL AND inicio_neoadjuvante IS NOT NULL
    """).fetchall()

    return [
        {"processo": r[0], "media_dias": round(r[1], 1) if r[1] else None}
        for r in result
    ]

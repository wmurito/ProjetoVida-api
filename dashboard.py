from sqlalchemy.orm import Session
from sqlalchemy import text, func
import models
import logging

logger = logging.getLogger(__name__)

# ✅ Distribuição por Estadiamento no Diagnóstico (SEGURO)
def get_estadiamento(db: Session):
    """Busca distribuição por estadiamento usando ORM seguro"""
    try:
        # Usar ORM para evitar SQL injection
        from sqlalchemy import case, literal
        
        result = db.query(
            func.coalesce(models.HistoriaDoenca.estadiamento_clinico, literal('Não informado')).label('estagio'),
            func.count(models.HistoriaDoenca.id).label('total')
        ).group_by(
            models.HistoriaDoenca.estadiamento_clinico
        ).order_by(
            func.count(models.HistoriaDoenca.id).desc()
        ).all()

        return [{"estagio": r.estagio, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar estadiamento: {str(e)}")
        return []


# ✅ Sobrevida Global (Vivo x Óbito) (SEGURO)
def get_sobrevida_global(db: Session):
    """Busca sobrevida global usando ORM seguro"""
    try:
        from sqlalchemy import literal
        
        result = db.query(
            func.coalesce(models.Desfecho.status_vital, literal('Não informado')).label('status'),
            func.count(models.Desfecho.id).label('total')
        ).group_by(
            models.Desfecho.status_vital
        ).all()

        return [{"status": r.status, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar sobrevida global: {str(e)}")
        return []


# ✅ Taxa de Recidiva (Local, Regional, Metástase) (SEGURO)
def get_taxa_recidiva(db: Session):
    """Busca taxa de recidiva usando ORM seguro"""
    try:
        from sqlalchemy import literal, union_all
        
        # Subqueries seguras
        recidiva_local = db.query(
            literal('Recidiva Local').label('tipo')
        ).filter(models.Desfecho.recidiva_local == True)
        
        recidiva_regional = db.query(
            literal('Recidiva Regional').label('tipo')
        ).filter(models.Desfecho.recidiva_regional == True)
        
        metastase = db.query(
            literal('Metástase').label('tipo')
        ).filter(
            models.Desfecho.metastases.isnot(None),
            models.Desfecho.metastases != '[]'
        )
        
        # Union das subqueries
        eventos = union_all(recidiva_local, recidiva_regional, metastase).alias('eventos')
        
        # Contar por tipo
        result = db.query(
            eventos.c.tipo,
            func.count().label('total')
        ).group_by(eventos.c.tipo).all()

        return [{"tipo": r.tipo, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar taxa de recidiva: {str(e)}")
        return []


# ✅ Média dos Tempos (Delta T) — entre diagnóstico, cirurgia, QT e RT (SEGURO)
def get_media_delta_t(db: Session):
    """Busca média dos tempos usando ORM seguro"""
    try:
        from sqlalchemy import literal, union_all, extract
        
        # Subquery 1: Diagnóstico → Cirurgia
        diag_cirurgia = db.query(
            literal('Diagnóstico → Cirurgia').label('processo'),
            func.avg(
                extract('day', models.TemposDiagnostico.data_cirurgia - models.TemposDiagnostico.data_diagnostico)
            ).label('media_dias')
        ).filter(
            models.TemposDiagnostico.data_cirurgia.isnot(None),
            models.TemposDiagnostico.data_diagnostico.isnot(None)
        )
        
        # Subquery 2: Diagnóstico → Início Tratamento
        diag_tratamento = db.query(
            literal('Diagnóstico → Início Tratamento').label('processo'),
            func.avg(
                extract('day', models.TemposDiagnostico.data_inicio_tratamento - models.TemposDiagnostico.data_diagnostico)
            ).label('media_dias')
        ).filter(
            models.TemposDiagnostico.data_inicio_tratamento.isnot(None),
            models.TemposDiagnostico.data_diagnostico.isnot(None)
        )
        
        # Subquery 3: Primeira Consulta → Diagnóstico
        consulta_diag = db.query(
            literal('Primeira Consulta → Diagnóstico').label('processo'),
            func.avg(
                extract('day', models.TemposDiagnostico.data_diagnostico - models.TemposDiagnostico.data_primeira_consulta)
            ).label('media_dias')
        ).filter(
            models.TemposDiagnostico.data_diagnostico.isnot(None),
            models.TemposDiagnostico.data_primeira_consulta.isnot(None)
        )
        
        # Union das subqueries
        tempos = union_all(diag_cirurgia, diag_tratamento, consulta_diag).alias('tempos')
        
        result = db.query(tempos).all()

        return [
            {"processo": r.processo, "media_dias": round(float(r.media_dias), 1) if r.media_dias else None}
            for r in result
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar média dos tempos: {str(e)}")
        return []

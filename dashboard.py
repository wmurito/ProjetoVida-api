from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_, literal, union_all, extract, cast, Date, distinct, Integer
import models
import logging

logger = logging.getLogger(__name__)

# ✅ 1. Distribuição por Estadiamento no Diagnóstico
def get_estadiamento(db: Session):
    """
    Busca distribuição por estadiamento.
    Ajuste: estadiamento_clinico foi movido para a tabela PACIENTE (campo hd_estadiamento_clinico).
    """
    try:
        # ATENÇÃO: Confirme se o mapeamento em models.Paciente.hd_estadiamento_clinico é o correto.
        estadiamento_field = models.Paciente.hd_estadiamento_clinico
        
        result = db.query(
            func.coalesce(estadiamento_field, literal('Não informado')).label('estagio'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            estadiamento_field
        ).order_by(
            func.count(models.Paciente.id_paciente).desc()
        ).all()

        return [{"estagio": r.estagio, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar estadiamento: {str(e)}")
        return []


# ✅ 2. Sobrevida Global (Vivo x Óbito)
def get_sobrevida_global(db: Session):
    """
    Busca sobrevida global.
    Ajuste: O campo status_vital permanece na tabela DESFECHO.
    """
    try:
        
        result = db.query(
            func.coalesce(models.Desfecho.status_vital, literal('Não informado')).label('status'),
            func.count(models.Desfecho.id_desfecho).label('total')
        ).group_by(
            models.Desfecho.status_vital
        ).all()

        return [{"status": r.status, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar sobrevida global: {str(e)}")
        return []


# ✅ 3. Taxa de Recidiva (Local, Regional, Metástase)
def get_taxa_recidiva(db: Session):
    """
    Busca taxa de recidiva.
    Ajuste: O campo `metastases` (array/list) foi substituído pela tabela 1:N
    `DESFECHO_METASTASES` (`models.DesfechoMetastases`).
    """
    try:
        
        # Subquery 1: Recidiva Local (usa o flag booleano em Desfecho)
        recidiva_local = db.query(
            models.Desfecho.id_desfecho.label('id'), # Identificador para o UNION ALL
            literal('Recidiva Local').label('tipo')
        ).filter(models.Desfecho.recidiva_local == True)
        
        # Subquery 2: Recidiva Regional (usa o flag booleano em Desfecho)
        recidiva_regional = db.query(
            models.Desfecho.id_desfecho.label('id'),
            literal('Recidiva Regional').label('tipo')
        ).filter(models.Desfecho.recidiva_regional == True)
        
        # Subquery 3: Metástase (JOIN com a nova tabela 1:N DESFECHO_METASTASES)
        # O distinct no SELECT evita contar locais duplicados na tabela de metástase, garantindo
        # que cada paciente seja contado apenas uma vez na categoria 'Metástase'.
        metastase = db.query(
            distinct(models.Desfecho.id_desfecho).label('id'),
            literal('Metástase').label('tipo')
        ).join(
            models.DesfechoMetastases,
            models.DesfechoMetastases.id_desfecho == models.Desfecho.id_desfecho
        )
        
        # Union das subqueries
        # Usamos o ID para garantir que pacientes duplicados sejam removidos no COUNT final (embora o GROUP BY já faça isso).
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


# ✅ 4. Média dos Tempos (Delta T)
def get_media_delta_t(db: Session):
    """
    Busca média dos tempos.
    Ajuste: Os campos de TemposDiagnostico foram movidos para a tabela DESFECHO.
    """
    try:
        # Referências aos novos campos na tabela DESFECHO (com prefixo 'td_')
        data_diag = models.Desfecho.td_data_diagnostico
        data_cir = models.Desfecho.td_data_cirurgia
        data_init_trat = models.Desfecho.td_data_inicio_tratamento
        data_prim_cons = models.Desfecho.td_data_primeira_consulta
        
        # Subquery 1: Diagnóstico → Cirurgia
        diag_cirurgia = db.query(
            literal('Diagnóstico → Cirurgia').label('processo'),
            func.avg(
                extract('day', cast(data_cir, Date) - cast(data_diag, Date))
            ).label('media_dias')
        ).filter(
            data_cir.isnot(None),
            data_diag.isnot(None)
        )
        
        # Subquery 2: Diagnóstico → Início Tratamento
        diag_tratamento = db.query(
            literal('Diagnóstico → Início Tratamento').label('processo'),
            func.avg(
                extract('day', cast(data_init_trat, Date) - cast(data_diag, Date))
            ).label('media_dias')
        ).filter(
            data_init_trat.isnot(None),
            data_diag.isnot(None)
        )
        
        # Subquery 3: Primeira Consulta → Diagnóstico
        consulta_diag = db.query(
            literal('Primeira Consulta → Diagnóstico').label('processo'),
            func.avg(
                extract('day', cast(data_diag, Date) - cast(data_prim_cons, Date))
            ).label('media_dias')
        ).filter(
            data_diag.isnot(None),
            data_prim_cons.isnot(None)
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


# ✅ 5. Distribuição por Gênero
def get_distribuicao_genero(db: Session):
    """
    Busca distribuição de pacientes por gênero.
    """
    try:
        result = db.query(
            func.coalesce(models.Paciente.genero, literal('Não informado')).label('genero'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            models.Paciente.genero
        ).order_by(
            func.count(models.Paciente.id_paciente).desc()
        ).all()

        return [{"genero": r.genero, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por gênero: {str(e)}")
        return []


# ✅ 6. Distribuição por Faixa Etária
def get_distribuicao_faixa_etaria(db: Session):
    """
    Busca distribuição de pacientes por faixa etária.
    """
    try:
        # Criar faixas etárias usando CASE WHEN
        faixa_etaria = func.case(
            (models.Paciente.idade < 30, '0-29 anos'),
            (and_(models.Paciente.idade >= 30, models.Paciente.idade < 40), '30-39 anos'),
            (and_(models.Paciente.idade >= 40, models.Paciente.idade < 50), '40-49 anos'),
            (and_(models.Paciente.idade >= 50, models.Paciente.idade < 60), '50-59 anos'),
            (and_(models.Paciente.idade >= 60, models.Paciente.idade < 70), '60-69 anos'),
            (models.Paciente.idade >= 70, '70+ anos'),
            else_='Não informado'
        ).label('faixa_etaria')

        result = db.query(
            faixa_etaria,
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            faixa_etaria
        ).order_by(
            func.count(models.Paciente.id_paciente).desc()
        ).all()

        return [{"faixa_etaria": r.faixa_etaria, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por faixa etária: {str(e)}")
        return []


# ✅ 7. Distribuição por Tipo de Cirurgia
def get_distribuicao_tipo_cirurgia(db: Session):
    """
    Busca distribuição por tipo de procedimento cirúrgico.
    """
    try:
        result = db.query(
            func.coalesce(models.TratamentoCirurgia.tipo_procedimento, literal('Não informado')).label('tipo'),
            func.count(models.TratamentoCirurgia.id_cirurgia).label('total')
        ).group_by(
            models.TratamentoCirurgia.tipo_procedimento
        ).order_by(
            func.count(models.TratamentoCirurgia.id_cirurgia).desc()
        ).all()

        return [{"tipo": r.tipo, "total": r.total} for r in result]
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por tipo de cirurgia: {str(e)}")
        return []


# ✅ 8. Distribuição por Marcadores Imunohistoquímicos
def get_distribuicao_marcadores(db: Session):
    """
    Busca distribuição por marcadores imunohistoquímicos.
    """
    try:
        # Buscar distribuição do HER2
        her2_result = db.query(
            func.coalesce(models.Imunohistoquimicas.her2, literal('Não informado')).label('marcador'),
            func.count(models.Imunohistoquimicas.id_imunohistoquimica).label('total')
        ).filter(
            models.Imunohistoquimicas.her2.isnot(None)
        ).group_by(
            models.Imunohistoquimicas.her2
        ).all()

        # Buscar distribuição do Ki67
        ki67_result = db.query(
            func.coalesce(models.Imunohistoquimicas.ki67, literal('Não informado')).label('marcador'),
            func.count(models.Imunohistoquimicas.id_imunohistoquimica).label('total')
        ).filter(
            models.Imunohistoquimicas.ki67.isnot(None)
        ).group_by(
            models.Imunohistoquimicas.ki67
        ).all()

        return {
            "her2": [{"marcador": r.marcador, "total": r.total} for r in her2_result],
            "ki67": [{"marcador": r.marcador, "total": r.total} for r in ki67_result]
        }
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por marcadores: {str(e)}")
        return {"her2": [], "ki67": []}


# ✅ 9. Distribuição por História Familiar
def get_distribuicao_historia_familiar(db: Session):
    """
    Busca distribuição por história familiar de câncer.
    """
    try:
        result = db.query(
            func.coalesce(models.Paciente.hf_cancer_familia, literal(False)).label('tem_historia'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            models.Paciente.hf_cancer_familia
        ).all()

        return [
            {"tem_historia": "Sim" if r.tem_historia else "Não", "total": r.total} 
            for r in result
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por história familiar: {str(e)}")
        return []


# ✅ 10. Distribuição por Hábitos de Vida
def get_distribuicao_habitos_vida(db: Session):
    """
    Busca distribuição por hábitos de vida (tabagismo, etilismo, atividade física).
    """
    try:
        # Tabagismo
        tabagismo_result = db.query(
            func.coalesce(models.Paciente.hv_tabagismo, literal('Não informado')).label('habito'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            models.Paciente.hv_tabagismo
        ).all()

        # Etilismo
        etilismo_result = db.query(
            func.coalesce(models.Paciente.hv_etilismo, literal('Não informado')).label('habito'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            models.Paciente.hv_etilismo
        ).all()

        # Atividade Física
        atividade_result = db.query(
            func.coalesce(models.Paciente.hv_atividade_fisica, literal('Não informado')).label('habito'),
            func.count(models.Paciente.id_paciente).label('total')
        ).group_by(
            models.Paciente.hv_atividade_fisica
        ).all()

        return {
            "tabagismo": [{"habito": r.habito, "total": r.total} for r in tabagismo_result],
            "etilismo": [{"habito": r.habito, "total": r.total} for r in etilismo_result],
            "atividade_fisica": [{"habito": r.habito, "total": r.total} for r in atividade_result]
        }
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição por hábitos de vida: {str(e)}")
        return {"tabagismo": [], "etilismo": [], "atividade_fisica": []}


# ✅ 11. Resumo Geral do Dashboard
def get_resumo_geral(db: Session):
    """
    Retorna um resumo geral com estatísticas principais.
    """
    try:
        # Total de pacientes
        total_pacientes = db.query(func.count(models.Paciente.id_paciente)).scalar() or 0
        
        # Pacientes com tratamento
        pacientes_com_tratamento = db.query(func.count(models.Tratamento.id_tratamento)).scalar() or 0
        
        # Pacientes com desfecho
        pacientes_com_desfecho = db.query(func.count(models.Desfecho.id_desfecho)).scalar() or 0
        
        # Pacientes vivos
        pacientes_vivos = db.query(func.count(models.Desfecho.id_desfecho)).filter(
            models.Desfecho.status_vital == 'Vivo'
        ).scalar() or 0
        
        # Pacientes com recidiva
        pacientes_recidiva = db.query(func.count(models.Desfecho.id_desfecho)).filter(
            or_(
                models.Desfecho.recidiva_local == True,
                models.Desfecho.recidiva_regional == True
            )
        ).scalar() or 0
        
        # Pacientes com metástase
        pacientes_metastase = db.query(func.count(models.Desfecho.id_desfecho)).filter(
            models.Desfecho.metastase_ocorreu == True
        ).scalar() or 0

        return {
            "total_pacientes": total_pacientes,
            "pacientes_com_tratamento": pacientes_com_tratamento,
            "pacientes_com_desfecho": pacientes_com_desfecho,
            "pacientes_vivos": pacientes_vivos,
            "pacientes_recidiva": pacientes_recidiva,
            "pacientes_metastase": pacientes_metastase,
            "taxa_sobrevida": round((pacientes_vivos / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0,
            "taxa_recidiva": round((pacientes_recidiva / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0,
            "taxa_metastase": round((pacientes_metastase / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0
        }
    except Exception as e:
        logger.error(f"Erro ao buscar resumo geral: {str(e)}")
        return {
            "total_pacientes": 0,
            "pacientes_com_tratamento": 0,
            "pacientes_com_desfecho": 0,
            "pacientes_vivos": 0,
            "pacientes_recidiva": 0,
            "pacientes_metastase": 0,
            "taxa_sobrevida": 0,
            "taxa_recidiva": 0,
            "taxa_metastase": 0
        }
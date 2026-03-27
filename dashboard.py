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
                cast(data_cir, Date) - cast(data_diag, Date)
            ).label('media_dias')
        ).filter(
            data_cir.isnot(None),
            data_diag.isnot(None)
        )
        
        # Subquery 2: Diagnóstico → Início Tratamento
        diag_tratamento = db.query(
            literal('Diagnóstico → Início Tratamento').label('processo'),
            func.avg(
                cast(data_init_trat, Date) - cast(data_diag, Date)
            ).label('media_dias')
        ).filter(
            data_init_trat.isnot(None),
            data_diag.isnot(None)
        )
        
        # Subquery 3: Primeira Consulta → Diagnóstico
        consulta_diag = db.query(
            literal('Primeira Consulta → Diagnóstico').label('processo'),
            func.avg(
                cast(data_diag, Date) - cast(data_prim_cons, Date)
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
    try:
        total_pacientes = db.query(func.count(models.Paciente.id_paciente)).scalar() or 0
        pacientes_com_tratamento = db.query(func.count(models.Tratamento.id_tratamento)).scalar() or 0
        pacientes_com_desfecho = db.query(func.count(models.Desfecho.id_desfecho)).scalar() or 0
        pacientes_vivos = db.query(func.count(models.Desfecho.id_desfecho)).filter(models.Desfecho.status_vital.ilike('%Vivo%')).scalar() or 0
        pacientes_obito = db.query(func.count(models.Desfecho.id_desfecho)).filter(
            or_(
                models.Desfecho.status_vital.ilike('%óbito%'),
                models.Desfecho.status_vital.ilike('%obito%'),
                models.Desfecho.morte == True
            )
        ).scalar() or 0
        pacientes_recidiva = db.query(func.count(models.Desfecho.id_desfecho)).filter(or_(models.Desfecho.recidiva_local == True, models.Desfecho.recidiva_regional == True)).scalar() or 0
        pacientes_metastase = db.query(func.count(models.Desfecho.id_desfecho)).filter(models.Desfecho.metastase_ocorreu == True).scalar() or 0
        
        # Idade média diagnóstico
        idade_media = db.query(func.avg(models.Paciente.hd_idade_diagnostico)).scalar()
        idade_media = float(idade_media) if idade_media else 0.0

        # Tamanho medio tumor
        tamanho_medio = db.query(func.avg(models.Paciente.hd_tamanho_tumoral_clinico)).scalar()
        tamanho_medio = float(tamanho_medio) if tamanho_medio else 0.0

        # Médias de Risco (Strings no DB -> Converte manual)
        riscos = db.query(models.Paciente.mp_score_gail, models.Paciente.mp_score_tyrer_cuzick).all()
        s_gail = 0.0
        c_gail = 0
        s_tyrer = 0.0
        c_tyrer = 0
        for g, t in riscos:
            if g:
                try: 
                    s_gail += float(g.replace('%', '').replace(',', '.').strip())
                    c_gail += 1
                except: pass
            if t:
                try: 
                    s_tyrer += float(t.replace('%', '').replace(',', '.').strip())
                    c_tyrer += 1
                except: pass

        return {
            "total_pacientes": total_pacientes,
            "pacientes_com_tratamento": pacientes_com_tratamento,
            "pacientes_com_desfecho": pacientes_com_desfecho,
            "pacientes_vivos": pacientes_vivos,
            "pacientes_obito": pacientes_obito,
            "pacientes_recidiva": pacientes_recidiva,
            "pacientes_metastase": pacientes_metastase,
            "taxa_sobrevida": round((pacientes_vivos / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0,
            "taxa_recidiva": round((pacientes_recidiva / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0,
            "taxa_metastase": round((pacientes_metastase / pacientes_com_desfecho * 100), 1) if pacientes_com_desfecho > 0 else 0,
            "idade_media_diagnostico": round(idade_media, 0),
            "tamanho_medio_tumor": round(tamanho_medio, 1),
            "media_risco_gail": round((s_gail / c_gail), 2) if c_gail > 0 else 0.0,
            "media_risco_tyrer": round((s_tyrer / c_tyrer), 2) if c_tyrer > 0 else 0.0,
        }
    except Exception as e:
        logger.error(f"Erro ao buscar resumo geral: {str(e)}")
        return {}


# ✅ 12. Estatísticas Temporais para Gráfico Área
def get_estatisticas_temporais(db: Session):
    import datetime
    try:
        hoje = datetime.date.today()
        meses = []
        new_pacients = []
        
        # Gera ultimos 6 meses
        for i in range(5, -1, -1):
            m = hoje.replace(day=1) - datetime.timedelta(days=i*30)
            mes = m.strftime('%b') # Jan, Feb
            meses.append(mes)
            new_pacients.append(0)
            
        return {
            "months": meses,
            "newPatients": new_pacients,
            "consultations": [0 for _ in meses]
        }
    except:
        return {"months": [], "newPatients": [], "consultations": []}

    
# ✅ 13. SUS Metrics (DeltaT, Estadiamento, Molecular) Direto do Banco!
def get_sus_metrics(db: Session):
    try:
        # 1. Delta T
        desfechos = db.query(models.Desfecho.td_data_diagnostico, models.Desfecho.td_data_inicio_tratamento).filter(
            models.Desfecho.td_data_diagnostico.isnot(None),
            models.Desfecho.td_data_inicio_tratamento.isnot(None)
        ).all()
        
        under30 = under60 = under90 = over90 = validDeltaTFound = 0
        for diag, trat in desfechos:
            diff_days = (trat - diag).days
            if diff_days >= 0:
                if diff_days <= 30: under30 += 1
                elif diff_days <= 60: under60 += 1
                elif diff_days <= 90: under90 += 1
                else: over90 += 1
                validDeltaTFound += 1

        # 2. Estadiamento
        est_0 = db.query(func.count(models.Paciente.id_paciente)).filter(models.Paciente.hd_estadiamento_clinico.ilike('%0%')).scalar() or 0
        est_1 = db.query(func.count(models.Paciente.id_paciente)).filter(models.Paciente.hd_estadiamento_clinico.ilike('%I%'), ~models.Paciente.hd_estadiamento_clinico.ilike('%II%'), ~models.Paciente.hd_estadiamento_clinico.ilike('%IV%')).scalar() or 0
        est_2 = db.query(func.count(models.Paciente.id_paciente)).filter(models.Paciente.hd_estadiamento_clinico.ilike('%II%'), ~models.Paciente.hd_estadiamento_clinico.ilike('%III%')).scalar() or 0
        est_3 = db.query(func.count(models.Paciente.id_paciente)).filter(models.Paciente.hd_estadiamento_clinico.ilike('%III%')).scalar() or 0
        est_4 = db.query(func.count(models.Paciente.id_paciente)).filter(models.Paciente.hd_estadiamento_clinico.ilike('%IV%')).scalar() or 0

        # 3. Molecular Count (Puxa do primeiro de tratamento)
        ihq = db.query(models.Imunohistoquimicas.re, models.Imunohistoquimicas.rp, models.Imunohistoquimicas.her2).all()
        luminal = her2 = tneg = indeterminado = 0
        for rec in ihq:
            re_pos = rec.re and ('pos' in rec.re.lower() or rec.re == 'P')
            rp_pos = rec.rp and ('pos' in rec.rp.lower() or rec.rp == 'P')
            rhPositivo = re_pos or rp_pos
            her2Positivo = rec.her2 and ('3+' in rec.her2 or 'pos' in rec.her2.lower())
            
            re_neg = rec.re and ('neg' in rec.re.lower() or rec.re == 'N')
            rp_neg = rec.rp and ('neg' in rec.rp.lower() or rec.rp == 'N')
            her2Negativo = rec.her2 and ('0' in rec.her2 or '1+' in rec.her2 or 'neg' in rec.her2.lower())
            
            if rhPositivo: luminal += 1
            elif her2Positivo and not rhPositivo: her2 += 1
            elif re_neg and rp_neg and her2Negativo: tneg += 1
            else: indeterminado += 1

        return {
            "deltaT": [
                { "name": '0 a 30 dias', "value": under30, "itemStyle": { "color": '#10b981' } },
                { "name": '31 a 60 dias\n(Alvo SUS)', "value": under60, "itemStyle": { "color": '#0ea5e9' } },
                { "name": '61 a 90 dias\n(Atraso Moderado)', "value": under90, "itemStyle": { "color": '#f59e0b' } },
                { "name": '> 90 dias\n(Atraso Grave)', "value": over90, "itemStyle": { "color": '#e11d48' } },
            ],
            "staging": [
                { "name": 'EC 0', "value": est_0 },
                { "name": 'EC I', "value": est_1 },
                { "name": 'EC II', "value": est_2 },
                { "name": 'EC III', "value": est_3 },
                { "name": 'EC IV', "value": est_4 }
            ],
            "molecular": [
                { "name": 'Luminal (RH+)', "value": luminal },
                { "name": 'HER2+', "value": her2 },
                { "name": 'Triplo Negativo', "value": tneg },
                { "name": 'Desconhecido', "value": indeterminado }
            ],
            "validDeltaTFound": validDeltaTFound
        }
    except Exception as e:
        logger.error(f"Erro ao buscar SUS metrics: {str(e)}")
        return {}
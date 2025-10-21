from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# =======================================================================
# SCHEMAS PARA FAMILIARES
# =======================================================================

class FamiliarBase(BaseModel):
    nome: Optional[str] = None
    parentesco: Optional[str] = None
    
    # CAMPOS DETALHADOS (CORRIGIDO)
    genero: Optional[str] = None
    tem_cancer_mama: Optional[bool] = False
    idade_cancer_mama: Optional[str] = None
    bilateral: Optional[bool] = False
    idade_segunda_mama: Optional[str] = None
    tem_cancer_ovario: Optional[bool] = False
    idade_cancer_ovario: Optional[str] = None
    gene_brca: Optional[str] = None
    tipo_cancer_outros: Optional[str] = None

class FamiliarCreate(FamiliarBase):
    pass

class Familiar(FamiliarBase):
    id_familiar: int
    id_paciente: int
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA TRATAMENTO - CIRURGIAS (UNIFICADAS)
# =======================================================================

class CirurgiaBase(BaseModel):
    tipo_procedimento: Optional[str] = None  # mama, axila, reconstrucao
    procedimento: Optional[str] = None
    data_cirurgia: Optional[date] = None

class CirurgiaCreate(CirurgiaBase):
    pass

class Cirurgia(CirurgiaBase):
    id_cirurgia: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA TRATAMENTO - TERAPIAS PALIATIVAS
# =======================================================================

class PalliativoQuimioterapiaBase(BaseModel):
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    sitio: Optional[str] = None  # CORRIGIDO: Campo 'sitio' faltante no ORM original
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class PalliativoQuimioterapiaCreate(PalliativoQuimioterapiaBase):
    pass

class PalliativoQuimioterapia(PalliativoQuimioterapiaBase):
    id_quimio_paliativa: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

class PalliativoRadioterapiaBase(BaseModel):
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class PalliativoRadioterapiaCreate(PalliativoRadioterapiaBase):
    pass

class PalliativoRadioterapia(PalliativoRadioterapiaBase):
    id_radio_paliativa: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

class PalliativoEndocrinoterapiaBase(BaseModel):
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class PalliativoEndocrinoterapiaCreate(PalliativoEndocrinoterapiaBase):
    pass

class PalliativoEndocrinoterapia(PalliativoEndocrinoterapiaBase):
    id_endo_paliativa: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

class PalliativoImunoterapiaBase(BaseModel):
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class PalliativoImunoterapiaCreate(PalliativoImunoterapiaBase):
    pass

class PalliativoImunoterapia(PalliativoImunoterapiaBase):
    id_imuno_paliativa: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA IMUNOHISTOQUÍMICAS
# =======================================================================

class ImunohistoquimicaBase(BaseModel):
    # CAMPOS COMPLETOS (CORRIGIDO)
    tipo: Optional[str] = None
    especime: Optional[str] = None
    data_realizacao: Optional[date] = None
    re: Optional[str] = None
    rp: Optional[str] = None
    ki67: Optional[str] = None
    her2: Optional[str] = None
    fish: Optional[str] = None
    outras_informacoes: Optional[str] = None

class ImunohistoquimicaCreate(ImunohistoquimicaBase):
    pass

class Imunohistoquimica(ImunohistoquimicaBase):
    id_imunohistoquimica: int
    id_tratamento: int
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA TRATAMENTO
# =======================================================================

class TratamentoBase(BaseModel):
    # CIRURGIA
    t_cirurgia_contexto_cirurgico: Optional[str] = None
    
    # QUIMIOTERAPIA NEADJUVANTE
    qt_neoadj_data_inicio: Optional[date] = None
    qt_neoadj_data_termino: Optional[date] = None
    qt_neoadj_esquema: Optional[str] = None
    qt_neoadj_intercorrencias: Optional[str] = None
    
    # QUIMIOTERAPIA ADJUVANTE
    qt_adj_data_inicio: Optional[date] = None
    qt_adj_data_termino: Optional[date] = None
    qt_adj_esquema: Optional[str] = None
    qt_adj_intercorrencias: Optional[str] = None
    
    # RADIOTERAPIA NEADJUVANTE
    rt_neoadj_data_inicio: Optional[date] = None
    rt_neoadj_data_termino: Optional[date] = None
    rt_neoadj_esquema: Optional[str] = None
    rt_neoadj_intercorrencias: Optional[str] = None
    
    # RADIOTERAPIA ADJUVANTE
    rt_adj_data_inicio: Optional[date] = None
    rt_adj_data_termino: Optional[date] = None
    rt_adj_esquema: Optional[str] = None
    rt_adj_intercorrencias: Optional[str] = None
    
    # ENDOCRINOTERAPIA NEADJUVANTE (CORRIGIDO prefixo de et_ para endo_)
    endo_neoadj_data_inicio: Optional[date] = None
    endo_neoadj_data_termino: Optional[date] = None
    endo_neoadj_esquema: Optional[str] = None
    endo_neoadj_intercorrencias: Optional[str] = None
    
    # ENDOCRINOTERAPIA ADJUVANTE (CORRIGIDO prefixo de et_ para endo_)
    endo_adj_data_inicio: Optional[date] = None
    endo_adj_data_termino: Optional[date] = None
    endo_adj_esquema: Optional[str] = None
    endo_adj_intercorrencias: Optional[str] = None
    
    # IMUNOTERAPIA NEADJUVANTE (CORRIGIDO prefixo de it_ para imuno_)
    imuno_neoadj_data_inicio: Optional[date] = None
    imuno_neoadj_data_termino: Optional[date] = None
    imuno_neoadj_esquema: Optional[str] = None
    imuno_neoadj_intercorrencias: Optional[str] = None
    
    # IMUNOTERAPIA ADJUVANTE (CORRIGIDO prefixo de it_ para imuno_)
    imuno_adj_data_inicio: Optional[date] = None
    imuno_adj_data_termino: Optional[date] = None
    imuno_adj_esquema: Optional[str] = None
    imuno_adj_intercorrencias: Optional[str] = None

    # CORE BIOPSY
    t_core_biopsy_realizada: Optional[bool] = False
    t_core_biopsy_data: Optional[date] = None
    t_core_biopsy_especime: Optional[str] = None
    t_core_biopsy_tecnica: Optional[str] = None
    t_core_biopsy_tipo_lesao: Optional[str] = None
    t_core_biopsy_anatomopatologico: Optional[str] = None
    t_core_biopsy_tipo_histologico: Optional[str] = None
    
    # MAMOTOMIA
    t_mamotomia_realizada: Optional[bool] = False
    t_mamotomia_data: Optional[date] = None
    t_mamotomia_especime: Optional[str] = None
    t_mamotomia_tecnica: Optional[str] = None
    t_mamotomia_tipo_lesao: Optional[str] = None
    t_mamotomia_anatomopatologico: Optional[str] = None
    t_mamotomia_tipo_histologico: Optional[str] = None
    
    # PAAF
    t_paaf_realizada: Optional[bool] = False
    t_paaf_data: Optional[date] = None
    t_paaf_especime: Optional[str] = None
    t_paaf_tecnica: Optional[str] = None
    t_paaf_achados: Optional[str] = None

class TratamentoCreate(TratamentoBase):
    # Relacionamentos 1:N (Simplificados para a melhor prática com 1 Tabela de Cirurgia)
    cirurgias: Optional[List[CirurgiaCreate]] = []
    quimio_paliativa: Optional[List[PalliativoQuimioterapiaCreate]] = []
    radio_paliativa: Optional[List[PalliativoRadioterapiaCreate]] = []
    endo_paliativa: Optional[List[PalliativoEndocrinoterapiaCreate]] = []
    imuno_paliativa: Optional[List[PalliativoImunoterapiaCreate]] = []
    imunohistoquimicas: Optional[List[ImunohistoquimicaCreate]] = []

class Tratamento(TratamentoBase):
    id_tratamento: int
    id_paciente: int
    
    # Relacionamentos 1:N (Simplificados para a melhor prática com 1 Tabela de Cirurgia)
    cirurgias: Optional[List[Cirurgia]] = []
    quimio_paliativa: Optional[List[PalliativoQuimioterapia]] = []
    radio_paliativa: Optional[List[PalliativoRadioterapia]] = []
    endo_paliativa: Optional[List[PalliativoEndocrinoterapia]] = []
    imuno_paliativa: Optional[List[PalliativoImunoterapia]] = []
    imunohistoquimicas: Optional[List[Imunohistoquimica]] = []
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA DESFECHO - METÁSTASES E EVENTOS
# =======================================================================

class MetastaseBase(BaseModel):
    local: Optional[str] = None

class MetastaseCreate(MetastaseBase):
    pass

class Metastase(MetastaseBase):
    id_desfecho_metastase: int
    id_desfecho: int
    
    class Config:
        orm_mode = True

class EventoBase(BaseModel):
    data: Optional[date] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    id_evento: int
    id_desfecho: int
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA DESFECHO
# =======================================================================

class DesfechoBase(BaseModel):
    # STATUS VITAL
    status_vital: Optional[str] = None
    morte: Optional[bool] = False  # CORRIGIDO: Campo faltante no ORM
    data_morte: Optional[date] = None
    causa_morte: Optional[str] = None
    
    # RECIDIVA / METÁSTASE
    recidiva_local: Optional[bool] = False
    data_recidiva_local: Optional[date] = None
    cirurgia_recidiva_local: Optional[str] = None
    recidiva_regional: Optional[bool] = False
    data_recidiva_regional: Optional[date] = None
    cirurgia_recidiva_regional: Optional[str] = None
    metastase_ocorreu: Optional[bool] = False

    # TEMPOS DE DIAGNÓSTICO (TD)
    td_data_primeira_consulta: Optional[date] = None
    td_data_diagnostico: Optional[date] = None
    td_data_inicio_tratamento: Optional[date] = None
    td_data_cirurgia: Optional[date] = None

class DesfechoCreate(DesfechoBase):
    # Relacionamentos 1:N
    metastases: Optional[List[MetastaseCreate]] = []
    eventos: Optional[List[EventoCreate]] = []

class Desfecho(DesfechoBase):
    id_desfecho: int
    id_paciente: int
    
    # Relacionamentos 1:N
    metastases: Optional[List[Metastase]] = []
    eventos: Optional[List[Evento]] = []
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA PACIENTE
# =======================================================================

class PacienteBase(BaseModel):
    # DADOS PESSOAIS E ENDEREÇO
    nome_completo: str
    data_nascimento: date
    genero: Optional[str] = None
    estado_civil: Optional[str] = None
    cor_etnia: Optional[str] = None
    escolaridade: Optional[str] = None
    renda_familiar: Optional[str] = None
    naturalidade: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    telefone: Optional[str] = None
    
    # DADOS FÍSICOS
    altura: Optional[float] = None
    peso: Optional[float] = None
    imc: Optional[float] = None
    idade: Optional[int] = None

    # HISTÓRIA PATOLÓGICA (HP)
    hp_has: Optional[bool] = False
    hp_diabetes: Optional[bool] = False
    hp_hipertensao: Optional[bool] = False
    hp_hipotireoidismo: Optional[bool] = False
    hp_ansiedade: Optional[bool] = False
    hp_depressao: Optional[bool] = False
    hp_doenca_cardiaca: Optional[bool] = False
    hp_doenca_renal: Optional[bool] = False
    hp_doenca_pulmonar: Optional[bool] = False
    hp_doenca_figado: Optional[bool] = False
    hp_avc: Optional[bool] = False
    hp_outra: Optional[str] = None
    hp_neoplasia_previa: Optional[bool] = False
    hp_qual_neoplasia: Optional[str] = None
    hp_idade_diagnostico_neoplasia: Optional[str] = None
    hp_biopsia_mamaria_previa: Optional[bool] = False
    hp_resultado_biopsia: Optional[str] = None

    # HISTÓRIA FAMILIAR (HF)
    hf_cancer_familia: Optional[bool] = False
    hf_observacoes: Optional[str] = None

    # HÁBITOS DE VIDA (HV)
    hv_tabagismo: Optional[str] = None
    hv_tabagismo_carga: Optional[str] = None
    hv_tabagismo_tempo_anos: Optional[str] = None
    hv_etilismo: Optional[str] = None
    hv_etilismo_tempo_anos: Optional[str] = None
    hv_etilismo_dose_diaria: Optional[str] = None
    hv_atividade_fisica: Optional[str] = None
    hv_tipo_atividade: Optional[str] = None
    hv_tempo_atividade_semanal_min: Optional[str] = None
    
    # PARIDADE (P)
    p_gesta: Optional[str] = None
    p_para: Optional[str] = None
    p_aborto: Optional[str] = None
    p_teve_filhos: Optional[bool] = False
    p_idade_primeiro_filho: Optional[str] = None
    p_amamentou: Optional[bool] = False
    p_tempo_amamentacao_meses: Optional[str] = None
    p_menarca_idade: Optional[str] = None
    p_menopausa: Optional[str] = None
    p_idade_menopausa: Optional[str] = None
    p_uso_trh: Optional[bool] = False
    p_tempo_uso_trh: Optional[str] = None
    p_tipo_terapia: Optional[str] = None  # CORRIGIDO: Campo faltante no ORM original
    p_uso_aco: Optional[bool] = False
    p_tempo_uso_aco: Optional[str] = None

    # HISTÓRIA DA DOENÇA (HD)
    hd_sinal_sintoma_principal: str
    hd_outro_sinal_sintoma: Optional[str] = None
    hd_data_sintomas: date
    hd_idade_diagnostico: int
    hd_ecog: Optional[str] = None
    hd_lado_acometido: str
    hd_tamanho_tumoral_clinico: Optional[float] = None
    hd_linfonodos_palpaveis: Optional[str] = None
    hd_estadiamento_clinico: Optional[str] = None
    hd_metastase_distancia: Optional[bool] = False
    hd_locais_metastase: Optional[str] = None

    # MODELOS PREDITORES (MP)
    mp_score_tyrer_cuzick: Optional[str] = None
    mp_score_canrisk: Optional[str] = None
    mp_score_gail: Optional[str] = None

class PacienteCreate(PacienteBase):
    # Relacionamentos 1:N
    familiares: Optional[List[FamiliarCreate]] = []
    
    # Relacionamentos 1:1
    tratamento: Optional[TratamentoCreate] = None
    desfecho: Optional[DesfechoCreate] = None

class Paciente(PacienteBase):
    id_paciente: int
    
    # Relacionamentos 1:N
    familiares: Optional[List[Familiar]] = []
    
    # Relacionamentos 1:1
    tratamento: Optional[Tratamento] = None
    desfecho: Optional[Desfecho] = None
    
    class Config:
        orm_mode = True

# =======================================================================
# SCHEMAS PARA HISTÓRICO
# =======================================================================

class PacienteHistorico(BaseModel):
    id: int
    id_paciente: int
    data_modificacao: datetime
    dados_anteriores: dict
    
    class Config:
        orm_mode = True
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Schemas para HistoriaPatologica
class HistoriaPatologicaBase(BaseModel):
    # Comorbidades
    has: Optional[bool] = False
    diabetes: Optional[bool] = False
    hipertensao: Optional[bool] = False
    doenca_cardiaca: Optional[bool] = False
    doenca_renal: Optional[bool] = False
    doenca_pulmonar: Optional[bool] = False
    doenca_figado: Optional[bool] = False
    avc: Optional[bool] = False
    outra: Optional[str] = None
    
    # Neoplasia prévia
    neoplasia_previa_has: Optional[bool] = False
    neoplasia_previa_qual: Optional[str] = None
    neoplasia_previa_idade_diagnostico: Optional[int] = None
    
    # Biópsia mamária prévia
    biopsia_mamaria_previa_has: Optional[bool] = False
    biopsia_mamaria_previa_resultado: Optional[str] = None

class HistoriaPatologicaCreate(HistoriaPatologicaBase):
    pass

class HistoriaPatologica(HistoriaPatologicaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para HistoriaFamiliar
class HistoriaFamiliarBase(BaseModel):
    cancer_familia: Optional[bool] = False
    observacoes: Optional[str] = None

class HistoriaFamiliarCreate(HistoriaFamiliarBase):
    pass

class HistoriaFamiliar(HistoriaFamiliarBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Familiar
class FamiliarBase(BaseModel):
    parentesco: Optional[str] = None
    tipo_cancer: Optional[str] = None
    idade_diagnostico: Optional[int] = None
    observacoes: Optional[str] = None

class FamiliarCreate(FamiliarBase):
    pass

class Familiar(FamiliarBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para HabitosDeVida
class HabitosDeVidaBase(BaseModel):
    # Tabagismo
    tabagismo: Optional[str] = 'nao'  # 'nao', 'sim', 'ex'
    tabagismo_carga: Optional[str] = None
    tabagismo_tempo_anos: Optional[str] = None
    
    # Etilismo
    etilismo: Optional[str] = 'nao'  # 'nao', 'sim', 'ex'
    etilismo_tempo_anos: Optional[str] = None
    
    # Atividade física
    atividade_fisica: Optional[str] = 'nao'  # 'nao', 'sim'
    tipo_atividade: Optional[str] = None
    tempo_atividade_semanal_min: Optional[str] = None

class HabitosDeVidaCreate(HabitosDeVidaBase):
    pass

class HabitosDeVida(HabitosDeVidaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Paridade
class ParidadeBase(BaseModel):
    # Paridade
    gesta: Optional[str] = None
    para: Optional[str] = None
    aborto: Optional[str] = None
    teve_filhos: Optional[bool] = False
    idade_primeiro_filho: Optional[str] = None
    
    # Amamentação
    amamentou: Optional[bool] = False
    tempo_amamentacao_meses: Optional[str] = None
    
    # Menstruação
    menarca_idade: Optional[str] = None
    menopausa: Optional[str] = 'nao'  # 'nao', 'sim', 'cirurgica'
    idade_menopausa: Optional[str] = None
    
    # Terapia hormonal
    uso_trh: Optional[bool] = False
    tempo_uso_trh: Optional[str] = None
    uso_aco: Optional[bool] = False
    tempo_uso_aco: Optional[str] = None

class ParidadeCreate(ParidadeBase):
    pass

class Paridade(ParidadeBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para HistoriaDoencaAtual
class HistoriaDoencaAtualBase(BaseModel):
    # Sintomas e diagnóstico
    sinal_sintoma_principal: Optional[str] = None
    outro_sinal_sintoma: Optional[str] = None
    data_sintomas: Optional[date] = None
    idade_diagnostico: Optional[int] = None
    ecog: Optional[str] = None
    lado_acometido: Optional[str] = None
    tamanho_tumoral_clinico: Optional[str] = None
    linfonodos_palpaveis: Optional[str] = 'nao'
    estadiamento_clinico: Optional[str] = None
    metastase_distancia: Optional[bool] = False
    locais_metastase: Optional[str] = None

class HistoriaDoencaAtualCreate(HistoriaDoencaAtualBase):
    pass

class HistoriaDoencaAtual(HistoriaDoencaAtualBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para ModelosPreditores
class ModelosPreditoresBase(BaseModel):
    score_tyrer_cuzick: Optional[float] = None
    score_canrisk: Optional[float] = None
    score_gail: Optional[float] = None

class ModelosPreditoresCreate(ModelosPreditoresBase):
    pass

class ModelosPreditores(ModelosPreditoresBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para CirurgiaMama
class CirurgiaMamaBase(BaseModel):
    data: Optional[date] = None
    tecnica: Optional[str] = None
    tipo_histologico: Optional[str] = None
    subtipo_histologico: Optional[str] = None
    tamanho_tumor: Optional[float] = None
    grau_histologico: Optional[str] = None
    margens: Optional[str] = None  # 'livres', 'comprometidas'
    margens_comprometidas_dimensao: Optional[float] = None
    linfonodos_excisados: Optional[int] = None
    linfonodos_comprometidos: Optional[int] = None
    invasao_extranodal: Optional[bool] = False
    invasao_extranodal_dimensao: Optional[float] = None
    imunohistoquimica: Optional[bool] = False
    imunohistoquimica_resultado: Optional[str] = None
    intercorrencias: Optional[str] = None

class CirurgiaMamaCreate(CirurgiaMamaBase):
    pass

class CirurgiaMama(CirurgiaMamaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para CirurgiaAxila
class CirurgiaAxilaBase(BaseModel):
    data: Optional[date] = None
    tecnica: Optional[str] = None
    tipo_histologico: Optional[str] = None
    subtipo_histologico: Optional[str] = None
    n_linfonodos_excisados: Optional[int] = None
    n_linfonodos_comprometidos: Optional[int] = None
    invasao_extranodal: Optional[bool] = False
    invasao_extranodal_dimensao: Optional[float] = None
    imunohistoquimica: Optional[bool] = False
    imunohistoquimica_resultado: Optional[str] = None
    intercorrencias: Optional[str] = None

class CirurgiaAxilaCreate(CirurgiaAxilaBase):
    pass

class CirurgiaAxila(CirurgiaAxilaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Reconstrucao
class ReconstrucaoBase(BaseModel):
    data: Optional[date] = None
    tecnica: Optional[str] = None
    intercorrencias: Optional[str] = None

class ReconstrucaoCreate(ReconstrucaoBase):
    pass

class Reconstrucao(ReconstrucaoBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Quimioterapia
class QuimioterapiaBase(BaseModel):
    tipo: Optional[str] = None  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class QuimioterapiaCreate(QuimioterapiaBase):
    pass

class Quimioterapia(QuimioterapiaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Radioterapia
class RadioterapiaBase(BaseModel):
    tipo: Optional[str] = None  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class RadioterapiaCreate(RadioterapiaBase):
    pass

class Radioterapia(RadioterapiaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Endocrinoterapia
class EndocrinoterapiaBase(BaseModel):
    tipo: Optional[str] = None  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class EndocrinoterapiaCreate(EndocrinoterapiaBase):
    pass

class Endocrinoterapia(EndocrinoterapiaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Imunoterapia
class ImunoterapiaBase(BaseModel):
    tipo: Optional[str] = None  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    esquema: Optional[str] = None
    intercorrencias: Optional[str] = None

class ImunoterapiaCreate(ImunoterapiaBase):
    pass

class Imunoterapia(ImunoterapiaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Imunohistoquimica
class ImunohistoquimicaBase(BaseModel):
    marcador: Optional[str] = None
    resultado: Optional[str] = None
    percentual: Optional[str] = None

class ImunohistoquimicaCreate(ImunohistoquimicaBase):
    pass

class Imunohistoquimica(ImunohistoquimicaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para CoreBiopsy
class CoreBiopsyBase(BaseModel):
    realizada: Optional[bool] = False
    data: Optional[date] = None
    especime: Optional[str] = None
    tecnica: Optional[str] = None
    tipo_lesao: Optional[str] = None
    anatomopatologico: Optional[str] = None
    tipo_histologico: Optional[str] = None

class CoreBiopsyCreate(CoreBiopsyBase):
    pass

class CoreBiopsy(CoreBiopsyBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Mamotomia
class MamotomiaBase(BaseModel):
    realizada: Optional[bool] = False
    data: Optional[date] = None
    especime: Optional[str] = None
    tecnica: Optional[str] = None
    tipo_lesao: Optional[str] = None
    anatomopatologico: Optional[str] = None
    tipo_histologico: Optional[str] = None

class MamotomiaCreate(MamotomiaBase):
    pass

class Mamotomia(MamotomiaBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Paaf
class PaafBase(BaseModel):
    realizada: Optional[bool] = False
    data: Optional[date] = None
    especime: Optional[str] = None
    tecnica: Optional[str] = None
    achados: Optional[str] = None

class PaafCreate(PaafBase):
    pass

class Paaf(PaafBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Desfecho
class DesfechoBase(BaseModel):
    # Status vital
    status_vital: Optional[str] = None  # 'vivo', 'morto'
    data_morte: Optional[date] = None
    causa_morte: Optional[str] = None
    
    # Recidivas
    recidiva_local: Optional[bool] = False
    data_recidiva_local: Optional[date] = None
    cirurgia_recidiva_local: Optional[str] = None
    recidiva_regional: Optional[bool] = False
    data_recidiva_regional: Optional[date] = None
    cirurgia_recidiva_regional: Optional[str] = None

class DesfechoCreate(DesfechoBase):
    pass

class Desfecho(DesfechoBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Metastase
class MetastaseBase(BaseModel):
    local: Optional[str] = None
    data_diagnostico: Optional[date] = None
    tratamento: Optional[str] = None
    observacoes: Optional[str] = None

class MetastaseCreate(MetastaseBase):
    pass

class Metastase(MetastaseBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para TemposDiagnostico
class TemposDiagnosticoBase(BaseModel):
    data_primeira_consulta: Optional[date] = None
    data_diagnostico: Optional[date] = None
    data_inicio_tratamento: Optional[date] = None
    data_cirurgia: Optional[date] = None

class TemposDiagnosticoCreate(TemposDiagnosticoBase):
    pass

class TemposDiagnostico(TemposDiagnosticoBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Evento
class EventoBase(BaseModel):
    data: Optional[date] = None
    descricao: Optional[str] = None
    observacoes: Optional[str] = None

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schema para PacienteHistorico
class PacienteHistoricoBase(BaseModel):
    dados_anteriores: dict
    data_modificacao: datetime

class PacienteHistorico(PacienteHistoricoBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True

# Schemas para Paciente
class PacienteBase(BaseModel):
    nome_completo: str
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    prontuario: Optional[str] = None
    genero: Optional[str] = None
    estado_civil: Optional[str] = None
    cor_etnia: Optional[str] = None
    escolaridade: Optional[str] = None
    renda_familiar: Optional[str] = None
    naturalidade: Optional[str] = None
    profissao: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    altura: Optional[float] = None
    peso: Optional[float] = None
    imc: Optional[float] = None
    idade: Optional[int] = None

class PacienteCreate(PacienteBase):
    historia_patologica: Optional[HistoriaPatologicaCreate] = None
    historia_familiar: Optional[HistoriaFamiliarCreate] = None
    familiares: Optional[List[FamiliarCreate]] = None
    habitos_vida: Optional[HabitosDeVidaCreate] = None
    paridade: Optional[ParidadeCreate] = None
    historia_doenca: Optional[HistoriaDoencaAtualCreate] = None
    modelos_preditores: Optional[ModelosPreditoresCreate] = None
    
    # Tratamento - Cirurgias
    cirurgias_mama: Optional[List[CirurgiaMamaCreate]] = None
    cirurgias_axila: Optional[List[CirurgiaAxilaCreate]] = None
    reconstrucoes: Optional[List[ReconstrucaoCreate]] = None
    
    # Tratamento - Terapias
    quimioterapias: Optional[List[QuimioterapiaCreate]] = None
    radioterapias: Optional[List[RadioterapiaCreate]] = None
    endocrinoterapias: Optional[List[EndocrinoterapiaCreate]] = None
    imunoterapias: Optional[List[ImunoterapiaCreate]] = None
    imunohistoquimicas: Optional[List[ImunohistoquimicaCreate]] = None
    
    # Procedimentos diagnósticos
    core_biopsies: Optional[List[CoreBiopsyCreate]] = None
    mamotomias: Optional[List[MamotomiaCreate]] = None
    paafs: Optional[List[PaafCreate]] = None
    
    # Evolução
    desfecho: Optional[DesfechoCreate] = None
    metastases: Optional[List[MetastaseCreate]] = None
    tempos_diagnostico: Optional[TemposDiagnosticoCreate] = None
    eventos: Optional[List[EventoCreate]] = None

class Paciente(PacienteBase):
    paciente_id: int
    historia_patologica: Optional[List[HistoriaPatologica]] = None
    historia_familiar: Optional[List[HistoriaFamiliar]] = None
    familiares: Optional[List[Familiar]] = None
    habitos_vida: Optional[List[HabitosDeVida]] = None
    paridade: Optional[List[Paridade]] = None
    historia_doenca: Optional[List[HistoriaDoencaAtual]] = None
    modelos_preditores: Optional[List[ModelosPreditores]] = None
    
    # Tratamento - Cirurgias
    cirurgias_mama: Optional[List[CirurgiaMama]] = None
    cirurgias_axila: Optional[List[CirurgiaAxila]] = None
    reconstrucoes: Optional[List[Reconstrucao]] = None
    
    # Tratamento - Terapias
    quimioterapias: Optional[List[Quimioterapia]] = None
    radioterapias: Optional[List[Radioterapia]] = None
    endocrinoterapias: Optional[List[Endocrinoterapia]] = None
    imunoterapias: Optional[List[Imunoterapia]] = None
    imunohistoquimicas: Optional[List[Imunohistoquimica]] = None
    
    # Procedimentos diagnósticos
    core_biopsies: Optional[List[CoreBiopsy]] = None
    mamotomias: Optional[List[Mamotomia]] = None
    paafs: Optional[List[Paaf]] = None
    
    # Evolução
    desfecho: Optional[List[Desfecho]] = None
    metastases: Optional[List[Metastase]] = None
    tempos_diagnostico: Optional[List[TemposDiagnostico]] = None
    eventos: Optional[List[Evento]] = None

    class Config:
        from_attributes = True

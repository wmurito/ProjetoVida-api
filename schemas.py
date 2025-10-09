from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# Historia Patologica
class HistoriaPatologicaBase(BaseModel):
    has: Optional[bool] = False
    diabetes: Optional[bool] = False
    hipertensao: Optional[bool] = False
    doenca_cardiaca: Optional[bool] = False
    doenca_renal: Optional[bool] = False
    doenca_pulmonar: Optional[bool] = False
    doenca_figado: Optional[bool] = False
    avc: Optional[bool] = False
    outra_comorbidade: Optional[str] = None
    neoplasia_previa: Optional[bool] = False
    qual_neoplasia: Optional[str] = None
    idade_diagnostico_neoplasia: Optional[int] = None
    biopsia_mamaria_previa: Optional[bool] = False
    resultado_biopsia: Optional[str] = None

class HistoriaPatologicaCreate(HistoriaPatologicaBase):
    pass

class HistoriaPatologica(HistoriaPatologicaBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Familiar
class FamiliarBase(BaseModel):
    parentesco: Optional[str] = None
    tipo_cancer: Optional[str] = None
    idade_diagnostico: Optional[int] = None

class FamiliarCreate(FamiliarBase):
    pass

class Familiar(FamiliarBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Habitos de Vida
class HabitosVidaBase(BaseModel):
    tabagismo: Optional[str] = "nao"
    tabagismo_carga: Optional[int] = None
    tabagismo_tempo_anos: Optional[int] = None
    etilismo: Optional[str] = "nao"
    etilismo_tempo_anos: Optional[int] = None
    atividade_fisica: Optional[str] = "nao"
    tipo_atividade: Optional[str] = None
    tempo_atividade_semanal_min: Optional[int] = None

class HabitosVidaCreate(HabitosVidaBase):
    pass

class HabitosVida(HabitosVidaBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Paridade
class ParidadeBase(BaseModel):
    gesta: Optional[int] = None
    para: Optional[int] = None
    aborto: Optional[int] = None
    teve_filhos: Optional[bool] = False
    idade_primeiro_filho: Optional[int] = None
    amamentou: Optional[bool] = False
    tempo_amamentacao_meses: Optional[int] = None
    menarca_idade: Optional[int] = None
    menopausa: Optional[str] = "nao"
    idade_menopausa: Optional[int] = None
    uso_trh: Optional[bool] = False
    tempo_uso_trh: Optional[int] = None
    uso_aco: Optional[bool] = False
    tempo_uso_aco: Optional[int] = None

class ParidadeCreate(ParidadeBase):
    pass

class Paridade(ParidadeBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Historia Doenca
class HistoriaDoencaBase(BaseModel):
    sinal_sintoma_principal: Optional[str] = None
    outro_sinal_sintoma: Optional[str] = None
    data_sintomas: Optional[date] = None
    idade_diagnostico: Optional[int] = None
    ecog: Optional[str] = None
    lado_acometido: Optional[str] = None
    tamanho_tumoral_clinico: Optional[float] = None
    linfonodos_palpaveis: Optional[str] = "nao"
    estadiamento_clinico: Optional[str] = None
    metastase_distancia: Optional[bool] = False
    locais_metastase: Optional[str] = None

class HistoriaDoencaCreate(HistoriaDoencaBase):
    pass

class HistoriaDoenca(HistoriaDoencaBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Modelos Preditores
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

# Tratamento
class TratamentoBase(BaseModel):
    cirurgia: Optional[dict] = None
    quimioterapia: Optional[dict] = None
    radioterapia: Optional[dict] = None
    endocrinoterapia: Optional[dict] = None
    imunoterapia: Optional[dict] = None
    imunohistoquimicas: Optional[list] = None
    core_biopsy: Optional[dict] = None
    mamotomia: Optional[dict] = None
    paaf: Optional[dict] = None

class TratamentoCreate(TratamentoBase):
    pass

class Tratamento(TratamentoBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Desfecho
class DesfechoBase(BaseModel):
    status_vital: Optional[str] = None
    data_morte: Optional[date] = None
    causa_morte: Optional[str] = None
    recidiva_local: Optional[bool] = False
    data_recidiva_local: Optional[date] = None
    cirurgia_recidiva_local: Optional[str] = None
    recidiva_regional: Optional[bool] = False
    data_recidiva_regional: Optional[date] = None
    cirurgia_recidiva_regional: Optional[str] = None
    metastases: Optional[list] = None

class DesfechoCreate(DesfechoBase):
    pass

class Desfecho(DesfechoBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Tempos Diagnostico
class TemposDiagnosticoBase(BaseModel):
    data_primeira_consulta: Optional[date] = None
    data_diagnostico: Optional[date] = None
    data_inicio_tratamento: Optional[date] = None
    data_cirurgia: Optional[date] = None
    eventos: Optional[list] = None

class TemposDiagnosticoCreate(TemposDiagnosticoBase):
    pass

class TemposDiagnostico(TemposDiagnosticoBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Paciente
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
    email: Optional[EmailStr] = None
    altura: Optional[float] = None
    peso: Optional[float] = None
    imc: Optional[float] = None
    idade: Optional[int] = None

class PacienteCreate(PacienteBase):
    historia_patologica: Optional[HistoriaPatologicaCreate] = None
    familiares: Optional[List[FamiliarCreate]] = []
    habitos_vida: Optional[HabitosVidaCreate] = None
    paridade: Optional[ParidadeCreate] = None
    historia_doenca: Optional[HistoriaDoencaCreate] = None
    modelos_preditores: Optional[ModelosPreditoresCreate] = None
    tratamento: Optional[TratamentoCreate] = None
    desfecho: Optional[DesfechoCreate] = None
    tempos_diagnostico: Optional[TemposDiagnosticoCreate] = None

class Paciente(PacienteBase):
    paciente_id: int
    historia_patologica: Optional[HistoriaPatologica] = None
    familiares: Optional[List[Familiar]] = []
    habitos_vida: Optional[HabitosVida] = None
    paridade: Optional[Paridade] = None
    historia_doenca: Optional[HistoriaDoenca] = None
    modelos_preditores: Optional[ModelosPreditores] = None
    tratamento: Optional[Tratamento] = None
    desfecho: Optional[Desfecho] = None
    tempos_diagnostico: Optional[TemposDiagnostico] = None
    
    class Config:
        from_attributes = True

# Historico
class PacienteHistorico(BaseModel):
    id: int
    paciente_id: int
    data_modificacao: datetime
    dados_anteriores: dict
    
    class Config:
        from_attributes = True

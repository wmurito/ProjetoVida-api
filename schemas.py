from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Schemas para HistoriaPatologica
class HistoriaPatologicaBase(BaseModel):
    hipertensao: Optional[bool] = None
    hipotireoidismo: Optional[bool] = None
    ansiedade: Optional[bool] = None
    depressao: Optional[bool] = None
    diabetes: Optional[bool] = None
    outros: Optional[str] = None

class HistoriaPatologicaCreate(HistoriaPatologicaBase):
    pass

class HistoriaPatologica(HistoriaPatologicaBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para HistoriaFamiliar
class HistoriaFamiliarBase(BaseModel):
    cancer_mama: Optional[bool] = None
    parentesco_mama: Optional[str] = None
    idade_diagnostico_mama: Optional[int] = None
    cancer_ovario: Optional[bool] = None
    parentesco_ovario: Optional[str] = None
    idade_diagnostico_ovario: Optional[int] = None
    outros: Optional[str] = None

class HistoriaFamiliarCreate(HistoriaFamiliarBase):
    pass

class HistoriaFamiliar(HistoriaFamiliarBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para HabitosDeVida
class HabitosDeVidaBase(BaseModel):
    tabagismo_carga: Optional[int] = None
    tabagismo_tempo_anos: Optional[int] = None
    etilismo_dose_diaria: Optional[str] = None
    etilismo_tempo_anos: Optional[int] = None

class HabitosDeVidaCreate(HabitosDeVidaBase):
    pass

class HabitosDeVida(HabitosDeVidaBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para Paridade
class ParidadeBase(BaseModel):
    gesta: Optional[int] = None
    para: Optional[int] = None
    aborto: Optional[int] = None
    idade_primeiro_filho: Optional[int] = None
    amamentou: Optional[bool] = None
    tempo_amamentacao_meses: Optional[int] = None
    menarca_idade: Optional[int] = None
    menopausa: Optional[bool] = None
    idade_menopausa: Optional[int] = None
    trh_uso: Optional[bool] = None
    tempo_uso_trh: Optional[int] = None
    tipo_terapia: Optional[str] = None

class ParidadeCreate(ParidadeBase):
    pass

class Paridade(ParidadeBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para HistoriaDoencaAtual
class HistoriaDoencaAtualBase(BaseModel):
    idade_diagnostico: Optional[int] = None
    score_tyrer_cuzick: Optional[float] = None
    score_canrisk: Optional[float] = None
    score_gail: Optional[float] = None

class HistoriaDoencaAtualCreate(HistoriaDoencaAtualBase):
    pass

class HistoriaDoencaAtual(HistoriaDoencaAtualBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para Histologia
class HistologiaBase(BaseModel):
    subtipo_core_re: Optional[str] = None
    subtipo_core_rp: Optional[str] = None
    subtipo_core_her2: Optional[str] = None
    subtipo_core_ki67: Optional[str] = None
    subtipo_cirurgia_re: Optional[str] = None
    subtipo_cirurgia_rp: Optional[str] = None
    subtipo_cirurgia_her2: Optional[str] = None
    subtipo_cirurgia_ki67: Optional[str] = None
    tamanho_tumoral: Optional[float] = None
    grau_tumoral_cirurgia: Optional[str] = None
    margens_comprometidas: Optional[bool] = None
    margens_local: Optional[str] = None
    biopsia_linfonodo_sentinela: Optional[bool] = None
    bls_numerador: Optional[int] = None
    bls_denominador: Optional[int] = None
    linfadenectomia_axilar: Optional[bool] = None
    ea_numerador: Optional[int] = None
    ea_denominador: Optional[int] = None

class HistologiaCreate(HistologiaBase):
    pass

class Histologia(HistologiaBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para Tratamento
class TratamentoBase(BaseModel):
    tratamento_neoadjuvante: Optional[bool] = None
    inicio_neoadjuvante: Optional[date] = None
    termino_neoadjuvante: Optional[date] = None
    qual_neoadjuvante: Optional[str] = None
    estagio_clinico_pre_qxt: Optional[str] = None
    imunoterapia: Optional[bool] = None
    adjuvancia: Optional[bool] = None
    quimioterapia: Optional[str] = None
    inicio_quimioterapia: Optional[date] = None
    fim_quimioterapia: Optional[date] = None
    radioterapia_tipo: Optional[str] = None
    radioterapia_sessoes: Optional[int] = None
    inicio_radioterapia: Optional[date] = None
    fim_radioterapia: Optional[date] = None
    endocrinoterapia: Optional[str] = None
    inicio_endocrino: Optional[date] = None
    fim_endocrino: Optional[date] = None
    terapia_alvo: Optional[str] = None
    inicio_terapia_alvo: Optional[date] = None
    fim_terapia_alvo: Optional[date] = None

class TratamentoCreate(TratamentoBase):
    pass

class Tratamento(TratamentoBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para Desfecho
class DesfechoBase(BaseModel):
    morte: Optional[bool] = None
    data_morte: Optional[date] = None
    causa_morte: Optional[str] = None
    metastase: Optional[bool] = None
    data_metastase: Optional[date] = None
    local_metastase: Optional[str] = None
    recidiva_local: Optional[bool] = None
    data_recidiva_local: Optional[date] = None
    recidiva_regional: Optional[bool] = None
    data_recidiva_regional: Optional[date] = None
    sitio_recidiva_regional: Optional[str] = None

class DesfechoCreate(DesfechoBase):
    pass

class Desfecho(DesfechoBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para TemposDiagnostico
class TemposDiagnosticoBase(BaseModel):
    data_mamografia: Optional[date] = None
    data_usg: Optional[date] = None
    data_rm: Optional[date] = None
    data_primeira_consulta: Optional[date] = None
    data_core_biopsy: Optional[date] = None
    data_cirurgia: Optional[date] = None

class TemposDiagnosticoCreate(TemposDiagnosticoBase):
    pass

class TemposDiagnostico(TemposDiagnosticoBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schema para PacienteHistorico
class PacienteHistoricoBase(BaseModel):
    dados_anteriores: dict
    data_modificacao: datetime

class PacienteHistorico(PacienteHistoricoBase):
    id: int
    paciente_id: int

    class Config:
        orm_mode = True

# Schemas para Paciente
class PacienteBase(BaseModel):
    nome_completo: str
    idade: Optional[int] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    naturalidade: Optional[str] = None
    altura: Optional[float] = None
    peso: Optional[float] = None
    imc: Optional[float] = None
    cor_etnia: Optional[str] = None
    escolaridade: Optional[str] = None
    renda_familiar: Optional[str] = None

class PacienteCreate(PacienteBase):
    historia_patologica: Optional[HistoriaPatologicaCreate] = None
    historia_familiar: Optional[HistoriaFamiliarCreate] = None
    habitos_vida: Optional[HabitosDeVidaCreate] = None
    paridade: Optional[ParidadeCreate] = None
    historia_doenca: Optional[HistoriaDoencaAtualCreate] = None
    histologia: Optional[HistologiaCreate] = None
    tratamento: Optional[TratamentoCreate] = None
    desfecho: Optional[DesfechoCreate] = None
    tempos_diagnostico: Optional[TemposDiagnosticoCreate] = None

class Paciente(PacienteBase):
    paciente_id: int
    historia_patologica: Optional[List[HistoriaPatologica]] = None
    historia_familiar: Optional[List[HistoriaFamiliar]] = None
    habitos_vida: Optional[List[HabitosDeVida]] = None
    paridade: Optional[List[Paridade]] = None
    historia_doenca: Optional[List[HistoriaDoencaAtual]] = None
    histologia: Optional[List[Histologia]] = None
    tratamento: Optional[List[Tratamento]] = None
    desfecho: Optional[List[Desfecho]] = None
    tempos_diagnostico: Optional[List[TemposDiagnostico]] = None

    class Config:
        orm_mode = True
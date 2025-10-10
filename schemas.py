from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# Historia Patologica
class HistoriaPatologicaBase(BaseModel):
    # Comorbidades - Estrutura achatada conforme frontend
    has: Optional[bool] = False
    diabetes: Optional[bool] = False
    hipertensao: Optional[bool] = False
    hipotireoidismo: Optional[bool] = False
    ansiedade: Optional[bool] = False
    depressao: Optional[bool] = False
    doenca_cardiaca: Optional[bool] = False
    doenca_renal: Optional[bool] = False
    doenca_pulmonar: Optional[bool] = False
    doenca_figado: Optional[bool] = False
    avc: Optional[bool] = False
    outra: Optional[str] = ""
    
    # Neoplasia prévia - Estrutura achatada conforme frontend
    neoplasia_previa: Optional[bool] = False
    qual_neoplasia: Optional[str] = ""
    idade_diagnostico_neoplasia: Optional[str] = ""
    
    # Biópsia mamária prévia - Estrutura achatada conforme frontend
    biopsia_mamaria_previa: Optional[bool] = False
    resultado_biopsia: Optional[str] = ""

class HistoriaPatologicaCreate(HistoriaPatologicaBase):
    pass

class HistoriaPatologica(HistoriaPatologicaBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Familiar
class HistoriaFamiliarBase(BaseModel):
    cancer_familia: Optional[bool] = False
    observacoes: Optional[str] = ""

class HistoriaFamiliarCreate(HistoriaFamiliarBase):
    pass

class HistoriaFamiliar(HistoriaFamiliarBase):
    id: int
    paciente_id: int

    class Config:
        from_attributes = True


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
    tabagismo_carga: Optional[str] = ""  # String conforme frontend
    tabagismo_tempo_anos: Optional[str] = ""  # String conforme frontend
    etilismo: Optional[str] = "nao"
    etilismo_tempo_anos: Optional[str] = ""  # String conforme frontend
    etilismo_dose_diaria: Optional[str] = ""
    atividade_fisica: Optional[str] = "nao"
    tipo_atividade: Optional[str] = ""  # String conforme frontend
    tempo_atividade_semanal_min: Optional[str] = ""  # String conforme frontend

class HabitosVidaCreate(HabitosVidaBase):
    pass

class HabitosVida(HabitosVidaBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Paridade
class ParidadeBase(BaseModel):
    gesta: Optional[str] = ""  # String conforme frontend
    para: Optional[str] = ""  # String conforme frontend
    aborto: Optional[str] = ""  # String conforme frontend
    teve_filhos: Optional[bool] = False
    idade_primeiro_filho: Optional[str] = ""  # String conforme frontend
    amamentou: Optional[bool] = False
    tempo_amamentacao_meses: Optional[str] = ""  # String conforme frontend
    menarca_idade: Optional[str] = ""  # String conforme frontend
    menopausa: Optional[str] = "nao"
    idade_menopausa: Optional[str] = ""  # String conforme frontend
    uso_trh: Optional[bool] = False  # Corrigido para 'uso_trh' conforme frontend
    tempo_uso_trh: Optional[str] = ""  # String conforme frontend
    uso_aco: Optional[bool] = False
    tempo_uso_aco: Optional[str] = ""  # String conforme frontend

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
    score_tyrer_cuzick: Optional[str] = ""  # String conforme JSON correto
    score_canrisk: Optional[str] = ""  # String conforme JSON correto
    score_gail: Optional[str] = ""  # String conforme JSON correto

class ModelosPreditoresCreate(ModelosPreditoresBase):
    pass

class ModelosPreditores(ModelosPreditoresBase):
    id: int
    paciente_id: int
    
    class Config:
        from_attributes = True

# Tratamento
class TratamentoBase(BaseModel):
    cirurgia: Optional[dict] = {
        "contexto_cirurgico": "",
        "mamas": [],
        "axilas": [],
        "reconstrucoes": []
    }
    quimioterapia: Optional[dict] = {
        "neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "paliativa": []
    }
    radioterapia: Optional[dict] = {
        "neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "paliativa": []
    }
    endocrinoterapia: Optional[dict] = {
        "neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "paliativa": []
    }
    imunoterapia: Optional[dict] = {
        "neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""},
        "paliativa": []
    }
    imunohistoquimicas: Optional[list] = []
    core_biopsy: Optional[dict] = {
        "realizada": False,
        "data": "",
        "especime": "",
        "tecnica": "",
        "tipo_lesao": "",
        "anatomopatologico": "",
        "tipo_histologico": ""
    }
    mamotomia: Optional[dict] = {
        "realizada": False,
        "data": "",
        "especime": "",
        "tecnica": "",
        "tipo_lesao": "",
        "anatomopatologico": "",
        "tipo_histologico": ""
    }
    paaf: Optional[dict] = {
        "realizada": False,
        "data": "",
        "especime": "",
        "tecnica": "",
        "achados": ""
    }

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
    metastase_ocorreu: Optional[bool] = False
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
    altura: Optional[float] = None
    peso: Optional[float] = None
    imc: Optional[float] = None
    idade: Optional[int] = None

class PacienteCreate(PacienteBase):
    historia_patologica: Optional[HistoriaPatologicaCreate] = None
    historia_familiar: Optional[HistoriaFamiliarCreate] = None
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
    historia_patologica: Optional[dict] = None
    historia_familiar: Optional[dict] = None
    familiares: Optional[List[dict]] = []
    habitos_vida: Optional[dict] = None
    paridade: Optional[dict] = None
    historia_doenca: Optional[dict] = None
    modelos_preditores: Optional[dict] = None
    tratamento: Optional[dict] = None
    desfecho: Optional[dict] = None
    tempos_diagnostico: Optional[dict] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Converter historia_patologica para estrutura achatada
        hp_dict = None
        if obj.historia_patologica:
            hp = obj.historia_patologica
            hp_dict = {
                "has": hp.has,
                "diabetes": hp.diabetes,
                "hipertensao": hp.hipertensao,
                "hipotireoidismo": hp.hipotireoidismo,
                "ansiedade": hp.ansiedade,
                "depressao": hp.depressao,
                "doenca_cardiaca": hp.doenca_cardiaca,
                "doenca_renal": hp.doenca_renal,
                "doenca_pulmonar": hp.doenca_pulmonar,
                "doenca_figado": hp.doenca_figado,
                "avc": hp.avc,
                "outra": hp.outra or "",
                "neoplasia_previa": hp.neoplasia_previa,
                "qual_neoplasia": hp.qual_neoplasia or "",
                "idade_diagnostico_neoplasia": hp.idade_diagnostico_neoplasia or "",
                "biopsia_mamaria_previa": hp.biopsia_mamaria_previa,
                "resultado_biopsia": hp.resultado_biopsia or ""
            }
        
        # Converter historia_familiar
        hf_dict = None
        if obj.historia_familiar:
            hf = obj.historia_familiar
            hf_dict = {
                "cancer_familia": hf.cancer_familia,
                "observacoes": hf.observacoes or ""
            }
        
        return cls(
            paciente_id=obj.paciente_id,
            nome_completo=obj.nome_completo,
            data_nascimento=obj.data_nascimento,
            genero=obj.genero,
            estado_civil=obj.estado_civil,
            cor_etnia=obj.cor_etnia,
            escolaridade=obj.escolaridade,
            renda_familiar=obj.renda_familiar,
            naturalidade=obj.naturalidade,
            cep=obj.cep,
            logradouro=obj.logradouro,
            numero=obj.numero,
            complemento=obj.complemento,
            bairro=obj.bairro,
            cidade=obj.cidade,
            uf=obj.uf,
            telefone=obj.telefone,
            altura=obj.altura,
            peso=obj.peso,
            imc=obj.imc,
            idade=obj.idade,
            historia_patologica=hp_dict,
            historia_familiar=hf_dict,
            familiares=[{"parentesco": f.parentesco, "tipo_cancer": f.tipo_cancer, "idade_diagnostico": f.idade_diagnostico} for f in obj.familiares] if obj.familiares else [],
            habitos_vida={k: v for k, v in obj.habitos_vida.__dict__.items() if not k.startswith('_')} if obj.habitos_vida else None,
            paridade={k: v for k, v in obj.paridade.__dict__.items() if not k.startswith('_')} if obj.paridade else None,
            historia_doenca={k: v for k, v in obj.historia_doenca.__dict__.items() if not k.startswith('_')} if obj.historia_doenca else None,
            modelos_preditores={k: v for k, v in obj.modelos_preditores.__dict__.items() if not k.startswith('_')} if obj.modelos_preditores else None,
            tratamento={
                "cirurgia": obj.tratamento.cirurgia or {"contexto_cirurgico": "", "mamas": [], "axilas": [], "reconstrucoes": []},
                "quimioterapia": obj.tratamento.quimioterapia or {"neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "paliativa": []},
                "radioterapia": obj.tratamento.radioterapia or {"neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "paliativa": []},
                "endocrinoterapia": obj.tratamento.endocrinoterapia or {"neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "paliativa": []},
                "imunoterapia": obj.tratamento.imunoterapia or {"neoadjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "adjuvante": {"data_inicio": "", "data_termino": "", "esquema": "", "intercorrencias": ""}, "paliativa": []},
                "imunohistoquimicas": obj.tratamento.imunohistoquimicas or [],
                "core_biopsy": obj.tratamento.core_biopsy or {"realizada": False, "data": "", "especime": "", "tecnica": "", "tipo_lesao": "", "anatomopatologico": "", "tipo_histologico": ""},
                "mamotomia": obj.tratamento.mamotomia or {"realizada": False, "data": "", "especime": "", "tecnica": "", "tipo_lesao": "", "anatomopatologico": "", "tipo_histologico": ""},
                "paaf": obj.tratamento.paaf or {"realizada": False, "data": "", "especime": "", "tecnica": "", "achados": ""}
            } if obj.tratamento else None,
            desfecho={k: v for k, v in obj.desfecho.__dict__.items() if not k.startswith('_')} if obj.desfecho else None,
            tempos_diagnostico={k: v for k, v in obj.tempos_diagnostico.__dict__.items() if not k.startswith('_')} if obj.tempos_diagnostico else None
        )

# Historico
class PacienteHistorico(BaseModel):
    id: int
    paciente_id: int
    data_modificacao: datetime
    dados_anteriores: dict
    
    class Config:
        from_attributes = True

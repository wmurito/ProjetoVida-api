from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
from security import encryption

class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = {"schema": "masto"}
    
    paciente_id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    nome_completo = Column(String(255), nullable=False)
    data_nascimento = Column(Date)
    cpf = Column(String(255), unique=True, index=True, nullable=True)  # Criptografado - temporariamente nullable
    prontuario = Column(String(50), unique=True, index=True)
    genero = Column(String(20))
    estado_civil = Column(String(50))
    cor_etnia = Column(String(50))
    escolaridade = Column(String(100))
    renda_familiar = Column(String(100))
    naturalidade = Column(String(100))
    profissao = Column(String(100))
    
    # Endereço
    cep = Column(String(10))
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    
    # Contato
    telefone = Column(String(20))
    email = Column(String(255))
    
    # Dados físicos
    altura = Column(Numeric(4, 2))
    peso = Column(Numeric(5, 2))
    imc = Column(Numeric(4, 2))
    idade = Column(Integer)
    
    # Relacionamentos
    historia_patologica = relationship("HistoriaPatologica", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    historia_familiar = relationship("HistoriaFamiliar", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    familiares = relationship("Familiar", back_populates="paciente", cascade="all, delete-orphan")
    habitos_vida = relationship("HabitosVida", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    paridade = relationship("Paridade", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    historia_doenca = relationship("HistoriaDoenca", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    modelos_preditores = relationship("ModelosPreditores", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    tratamento = relationship("Tratamento", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    desfecho = relationship("Desfecho", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    tempos_diagnostico = relationship("TemposDiagnostico", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    historico = relationship("PacienteHistorico", back_populates="paciente", cascade="all, delete-orphan")


class HistoriaPatologica(Base):
    __tablename__ = "historia_patologica"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    # Comorbidades - Estrutura aninhada conforme frontend
    comorbidades_has = Column(Boolean, default=False)
    comorbidades_diabetes = Column(Boolean, default=False)
    comorbidades_hipertensao = Column(Boolean, default=False)
    comorbidades_doenca_cardiaca = Column(Boolean, default=False)
    comorbidades_doenca_renal = Column(Boolean, default=False)
    comorbidades_doenca_pulmonar = Column(Boolean, default=False)
    comorbidades_doenca_figado = Column(Boolean, default=False)
    comorbidades_avc = Column(Boolean, default=False)
    comorbidades_outra = Column(String(255))
    
    # Neoplasia prévia - Estrutura aninhada conforme frontend
    neoplasia_previa_has = Column(Boolean, default=False)
    neoplasia_previa_qual = Column(String(255))
    neoplasia_previa_idade_diagnostico = Column(Integer)
    
    # Biópsia mamária prévia - Estrutura aninhada conforme frontend
    biopsia_mamaria_previa_has = Column(Boolean, default=False)
    biopsia_mamaria_previa_resultado = Column(String(255))
    
    paciente = relationship("Paciente", back_populates="historia_patologica")


class HistoriaFamiliar(Base):
    __tablename__ = "historia_familiar"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    cancer_familia = Column(Boolean, default=False)
    observacoes = Column(String(500))
    
    paciente = relationship("Paciente", back_populates="historia_familiar")


class Familiar(Base):
    __tablename__ = "familiar"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    parentesco = Column(String(100))
    tipo_cancer = Column(String(100))
    idade_diagnostico = Column(Integer)
    
    paciente = relationship("Paciente", back_populates="familiares")


class HabitosVida(Base):
    __tablename__ = "habitos_vida"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    tabagismo = Column(String(20))
    tabagismo_carga = Column(String(50))  # String conforme frontend
    tabagismo_tempo_anos = Column(String(50))  # String conforme frontend
    
    etilismo = Column(String(20))
    etilismo_tempo_anos = Column(String(50))  # String conforme frontend
    
    atividade_fisica = Column(String(20))
    tipo_atividade = Column(String(255))  # Corrigido para 'tipo_atividade' conforme frontend
    tempo_atividade_semanal_min = Column(String(50))  # String conforme frontend
    
    paciente = relationship("Paciente", back_populates="habitos_vida")


class Paridade(Base):
    __tablename__ = "paridade"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    gesta = Column(String(50))  # String conforme frontend
    para = Column(String(50))  # String conforme frontend
    aborto = Column(String(50))  # String conforme frontend
    teve_filhos = Column(Boolean, default=False)
    idade_primeiro_filho = Column(String(50))  # String conforme frontend
    
    amamentou = Column(Boolean, default=False)
    tempo_amamentacao_meses = Column(String(50))  # String conforme frontend
    
    menarca_idade = Column(String(50))  # String conforme frontend
    menopausa = Column(String(20))
    idade_menopausa = Column(String(50))  # String conforme frontend
    
    uso_trh = Column(Boolean, default=False)  # Corrigido para 'uso_trh' conforme frontend
    tempo_uso_trh = Column(String(50))  # String conforme frontend
    
    uso_aco = Column(Boolean, default=False)
    tempo_uso_aco = Column(String(50))  # String conforme frontend
    
    paciente = relationship("Paciente", back_populates="paridade")


class HistoriaDoenca(Base):
    __tablename__ = "historia_doenca"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    sinal_sintoma_principal = Column(String(255))
    outro_sinal_sintoma = Column(String(255))
    data_sintomas = Column(Date)
    idade_diagnostico = Column(String(50))  # String conforme JSON correto
    
    ecog = Column(String(10))
    lado_acometido = Column(String(20))
    tamanho_tumoral_clinico = Column(String(50))  # String conforme JSON correto
    linfonodos_palpaveis = Column(String(20))
    estadiamento_clinico = Column(String(50))
    
    metastase_distancia = Column(Boolean, default=False)
    locais_metastase = Column(Text)
    
    paciente = relationship("Paciente", back_populates="historia_doenca")


class ModelosPreditores(Base):
    __tablename__ = "modelos_preditores"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    score_tyrer_cuzick = Column(String(50))  # String conforme JSON correto
    score_canrisk = Column(String(50))  # String conforme JSON correto
    score_gail = Column(String(50))  # String conforme JSON correto
    
    paciente = relationship("Paciente", back_populates="modelos_preditores")


class Tratamento(Base):
    __tablename__ = "tratamento"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    # Armazenar como JSON para flexibilidade
    cirurgia = Column(JSON)
    quimioterapia = Column(JSON)
    radioterapia = Column(JSON)
    endocrinoterapia = Column(JSON)
    imunoterapia = Column(JSON)
    imunohistoquimicas = Column(JSON)
    core_biopsy = Column(JSON)
    mamotomia = Column(JSON)
    paaf = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="tratamento")


class Desfecho(Base):
    __tablename__ = "desfecho"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    status_vital = Column(String(50))
    data_morte = Column(Date)
    causa_morte = Column(String(255))
    recidiva_local = Column(Boolean, default=False)
    data_recidiva_local = Column(Date)
    cirurgia_recidiva_local = Column(String(255))
    
    recidiva_regional = Column(Boolean, default=False)
    data_recidiva_regional = Column(Date)
    cirurgia_recidiva_regional = Column(String(255))
    
    metastases = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="desfecho")


class TemposDiagnostico(Base):
    __tablename__ = "tempos_diagnostico"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    data_primeira_consulta = Column(Date)
    data_diagnostico = Column(Date)
    data_inicio_tratamento = Column(Date)
    data_cirurgia = Column(Date)
    eventos = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="tempos_diagnostico")


class PacienteHistorico(Base):
    __tablename__ = "paciente_historico"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data_modificacao = Column(DateTime, default=datetime.datetime.utcnow)
    dados_anteriores = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="historico")

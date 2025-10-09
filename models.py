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
    cpf = Column(String(255), unique=True, index=True)  # Criptografado
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
    
    # Comorbidades
    has = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    hipertensao = Column(Boolean, default=False)
    doenca_cardiaca = Column(Boolean, default=False)
    doenca_renal = Column(Boolean, default=False)
    doenca_pulmonar = Column(Boolean, default=False)
    doenca_figado = Column(Boolean, default=False)
    avc = Column(Boolean, default=False)
    outra_comorbidade = Column(String(255))
    
    # Neoplasia prévia
    neoplasia_previa = Column(Boolean, default=False)
    qual_neoplasia = Column(String(255))
    idade_diagnostico_neoplasia = Column(Integer)
    
    # Biópsia mamária prévia
    biopsia_mamaria_previa = Column(Boolean, default=False)
    resultado_biopsia = Column(String(255))
    
    paciente = relationship("Paciente", back_populates="historia_patologica")


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
    tabagismo_carga = Column(Integer)
    tabagismo_tempo_anos = Column(Integer)
    
    etilismo = Column(String(20))
    etilismo_tempo_anos = Column(Integer)
    
    atividade_fisica = Column(String(20))
    tipo_atividade = Column(String(255))
    tempo_atividade_semanal_min = Column(Integer)
    
    paciente = relationship("Paciente", back_populates="habitos_vida")


class Paridade(Base):
    __tablename__ = "paridade"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    gesta = Column(Integer)
    para = Column(Integer)
    aborto = Column(Integer)
    teve_filhos = Column(Boolean, default=False)
    idade_primeiro_filho = Column(Integer)
    
    amamentou = Column(Boolean, default=False)
    tempo_amamentacao_meses = Column(Integer)
    
    menarca_idade = Column(Integer)
    menopausa = Column(String(20))
    idade_menopausa = Column(Integer)
    
    uso_trh = Column(Boolean, default=False)
    tempo_uso_trh = Column(Integer)
    
    uso_aco = Column(Boolean, default=False)
    tempo_uso_aco = Column(Integer)
    
    paciente = relationship("Paciente", back_populates="paridade")


class HistoriaDoenca(Base):
    __tablename__ = "historia_doenca"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"), unique=True)
    
    sinal_sintoma_principal = Column(String(255))
    outro_sinal_sintoma = Column(String(255))
    data_sintomas = Column(Date)
    idade_diagnostico = Column(Integer)
    
    ecog = Column(String(10))
    lado_acometido = Column(String(20))
    tamanho_tumoral_clinico = Column(Numeric(5, 2))
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
    
    score_tyrer_cuzick = Column(Numeric(5, 2))
    score_canrisk = Column(Numeric(5, 2))
    score_gail = Column(Numeric(5, 2))
    
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

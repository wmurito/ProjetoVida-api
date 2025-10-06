from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, Table, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class PacienteHistorico(Base):
    __tablename__ = "paciente_historico"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data_modificacao = Column(DateTime, default=datetime.datetime.utcnow)
    dados_anteriores = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="historico")

class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = {"schema": "masto"}
    
    paciente_id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(255), nullable=False)
    idade = Column(Integer)
    endereco = Column(String(255))
    cidade = Column(String(100))
    data_nascimento = Column(Date)
    telefone = Column(String(20))
    naturalidade = Column(String(100))
    altura = Column(Numeric(4, 2))
    peso = Column(Numeric(5, 2))
    imc = Column(Numeric(4, 2))
    cor_etnia = Column(String(20))
    escolaridade = Column(String(50))
    renda_familiar = Column(String(50))

    # Relacionamentos
    historia_patologica = relationship("HistoriaPatologica", back_populates="paciente", cascade="all, delete")
    historia_familiar = relationship("HistoriaFamiliar", back_populates="paciente", cascade="all, delete")
    habitos_vida = relationship("HabitosDeVida", back_populates="paciente", cascade="all, delete")
    paridade = relationship("Paridade", back_populates="paciente", cascade="all, delete")
    historia_doenca = relationship("HistoriaDoencaAtual", back_populates="paciente", cascade="all, delete")
    histologia = relationship("Histologia", back_populates="paciente", cascade="all, delete")
    tratamento = relationship("Tratamento", back_populates="paciente", cascade="all, delete")
    desfecho = relationship("Desfecho", back_populates="paciente", cascade="all, delete")
    tempos_diagnostico = relationship("TemposDiagnostico", back_populates="paciente", cascade="all, delete")
    historico = relationship("PacienteHistorico", back_populates="paciente", cascade="all, delete")


class HistoriaPatologica(Base):
    __tablename__ = "historia_patologica"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    hipertensao = Column(Boolean)
    hipotireoidismo = Column(Boolean)
    ansiedade = Column(Boolean)
    depressao = Column(Boolean)
    diabetes = Column(Boolean)
    outros = Column(String(255))

    paciente = relationship("Paciente", back_populates="historia_patologica")


class HistoriaFamiliar(Base):
    __tablename__ = "historia_familiar"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    cancer_mama = Column(Boolean)
    parentesco_mama = Column(String(100))
    idade_diagnostico_mama = Column(Integer)
    cancer_ovario = Column(Boolean)
    parentesco_ovario = Column(String(100))
    idade_diagnostico_ovario = Column(Integer)
    outros = Column(String(255))

    paciente = relationship("Paciente", back_populates="historia_familiar")


class HabitosDeVida(Base):
    __tablename__ = "habitos_de_vida"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tabagismo_carga = Column(Integer)
    tabagismo_tempo_anos = Column(Integer)
    etilismo_dose_diaria = Column(String(100))
    etilismo_tempo_anos = Column(Integer)

    paciente = relationship("Paciente", back_populates="habitos_vida")


class Paridade(Base):
    __tablename__ = "paridade"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    gesta = Column(Integer)
    para = Column(Integer)
    aborto = Column(Integer)
    idade_primeiro_filho = Column(Integer)
    amamentou = Column(Boolean)
    tempo_amamentacao_meses = Column(Integer)
    menarca_idade = Column(Integer)
    menopausa = Column(Boolean)
    idade_menopausa = Column(Integer)
    trh_uso = Column(Boolean)
    tempo_uso_trh = Column(Integer)
    tipo_terapia = Column(String(255))

    paciente = relationship("Paciente", back_populates="paridade")


class HistoriaDoencaAtual(Base):
    __tablename__ = "historia_doenca_atual"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    idade_diagnostico = Column(Integer)
    score_tyrer_cuzick = Column(Numeric(5, 2))
    score_canrisk = Column(Numeric(5, 2))
    score_gail = Column(Numeric(5, 2))

    paciente = relationship("Paciente", back_populates="historia_doenca")


class Histologia(Base):
    __tablename__ = "histologia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    subtipo_core_re = Column(String(10))
    subtipo_core_rp = Column(String(10))
    subtipo_core_her2 = Column(String(10))
    subtipo_core_ki67 = Column(String(10))
    subtipo_cirurgia_re = Column(String(10))
    subtipo_cirurgia_rp = Column(String(10))
    subtipo_cirurgia_her2 = Column(String(10))
    subtipo_cirurgia_ki67 = Column(String(10))
    tamanho_tumoral = Column(Numeric(5, 2))
    grau_tumoral_cirurgia = Column(String(50))
    margens_comprometidas = Column(Boolean)
    margens_local = Column(String(100))
    biopsia_linfonodo_sentinela = Column(Boolean)
    bls_numerador = Column(Integer)
    bls_denominador = Column(Integer)
    linfadenectomia_axilar = Column(Boolean)
    ea_numerador = Column(Integer)
    ea_denominador = Column(Integer)

    paciente = relationship("Paciente", back_populates="histologia")


class Tratamento(Base):
    __tablename__ = "tratamento"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tratamento_neoadjuvante = Column(Boolean)
    inicio_neoadjuvante = Column(Date)
    termino_neoadjuvante = Column(Date)
    qual_neoadjuvante = Column(String(255))
    estagio_clinico_pre_qxt = Column(String(50))
    imunoterapia = Column(Boolean)
    adjuvancia = Column(Boolean)
    quimioterapia = Column(String(255))
    inicio_quimioterapia = Column(Date)
    fim_quimioterapia = Column(Date)
    radioterapia_tipo = Column(String(100))
    radioterapia_sessoes = Column(Integer)
    inicio_radioterapia = Column(Date)
    fim_radioterapia = Column(Date)
    endocrinoterapia = Column(String(255))
    inicio_endocrino = Column(Date)
    fim_endocrino = Column(Date)
    terapia_alvo = Column(String(255))
    inicio_terapia_alvo = Column(Date)
    fim_terapia_alvo = Column(Date)

    paciente = relationship("Paciente", back_populates="tratamento")


class Desfecho(Base):
    __tablename__ = "desfecho"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    morte = Column(Boolean)
    data_morte = Column(Date)
    causa_morte = Column(String(255))
    metastase = Column(Boolean)
    data_metastase = Column(Date)
    local_metastase = Column(String(255))
    recidiva_local = Column(Boolean)
    data_recidiva_local = Column(Date)
    recidiva_regional = Column(Boolean)
    data_recidiva_regional = Column(Date)
    sitio_recidiva_regional = Column(String(255))

    paciente = relationship("Paciente", back_populates="desfecho")


class TemposDiagnostico(Base):
    __tablename__ = "tempos_diagnostico"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data_mamografia = Column(Date)
    data_usg = Column(Date)
    data_rm = Column(Date)
    data_primeira_consulta = Column(Date)
    data_core_biopsy = Column(Date)
    data_cirurgia = Column(Date)

    paciente = relationship("Paciente", back_populates="tempos_diagnostico")
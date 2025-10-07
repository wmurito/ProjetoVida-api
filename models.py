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
    data_nascimento = Column(Date)
    cpf = Column(String(14))
    prontuario = Column(String(50))
    genero = Column(String(20))
    estado_civil = Column(String(50))
    cor_etnia = Column(String(20))
    escolaridade = Column(String(50))
    renda_familiar = Column(String(50))
    naturalidade = Column(String(100))
    profissao = Column(String(100))
    cep = Column(String(10))
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    telefone = Column(String(20))
    email = Column(String(255))
    altura = Column(Numeric(4, 2))
    peso = Column(Numeric(5, 2))
    imc = Column(Numeric(4, 2))
    idade = Column(Integer)

    # Relacionamentos
    historia_patologica = relationship("HistoriaPatologica", back_populates="paciente", cascade="all, delete")
    historia_familiar = relationship("HistoriaFamiliar", back_populates="paciente", cascade="all, delete")
    familiares = relationship("Familiar", back_populates="paciente", cascade="all, delete")
    habitos_vida = relationship("HabitosDeVida", back_populates="paciente", cascade="all, delete")
    paridade = relationship("Paridade", back_populates="paciente", cascade="all, delete")
    historia_doenca = relationship("HistoriaDoencaAtual", back_populates="paciente", cascade="all, delete")
    modelos_preditores = relationship("ModelosPreditores", back_populates="paciente", cascade="all, delete")
    
    # Tratamento - Cirurgias
    cirurgias_mama = relationship("CirurgiaMama", back_populates="paciente", cascade="all, delete")
    cirurgias_axila = relationship("CirurgiaAxila", back_populates="paciente", cascade="all, delete")
    reconstrucoes = relationship("Reconstrucao", back_populates="paciente", cascade="all, delete")
    
    # Tratamento - Terapias
    quimioterapias = relationship("Quimioterapia", back_populates="paciente", cascade="all, delete")
    radioterapias = relationship("Radioterapia", back_populates="paciente", cascade="all, delete")
    endocrinoterapias = relationship("Endocrinoterapia", back_populates="paciente", cascade="all, delete")
    imunoterapias = relationship("Imunoterapia", back_populates="paciente", cascade="all, delete")
    imunohistoquimicas = relationship("Imunohistoquimica", back_populates="paciente", cascade="all, delete")
    
    # Procedimentos diagnósticos
    core_biopsies = relationship("CoreBiopsy", back_populates="paciente", cascade="all, delete")
    mamotomias = relationship("Mamotomia", back_populates="paciente", cascade="all, delete")
    paafs = relationship("Paaf", back_populates="paciente", cascade="all, delete")
    
    # Evolução
    desfecho = relationship("Desfecho", back_populates="paciente", cascade="all, delete")
    metastases = relationship("Metastase", back_populates="paciente", cascade="all, delete")
    tempos_diagnostico = relationship("TemposDiagnostico", back_populates="paciente", cascade="all, delete")
    eventos = relationship("Evento", back_populates="paciente", cascade="all, delete")
    historico = relationship("PacienteHistorico", back_populates="paciente", cascade="all, delete")


class HistoriaPatologica(Base):
    __tablename__ = "historia_patologica"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    # Comorbidades
    has = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    hipertensao = Column(Boolean, default=False)
    doenca_cardiaca = Column(Boolean, default=False)
    doenca_renal = Column(Boolean, default=False)
    doenca_pulmonar = Column(Boolean, default=False)
    doenca_figado = Column(Boolean, default=False)
    avc = Column(Boolean, default=False)
    outra = Column(String(255))
    
    # Neoplasia prévia
    neoplasia_previa_has = Column(Boolean, default=False)
    neoplasia_previa_qual = Column(String(255))
    neoplasia_previa_idade_diagnostico = Column(Integer)
    
    # Biópsia mamária prévia
    biopsia_mamaria_previa_has = Column(Boolean, default=False)
    biopsia_mamaria_previa_resultado = Column(String(255))

    paciente = relationship("Paciente", back_populates="historia_patologica")


class HistoriaFamiliar(Base):
    __tablename__ = "historia_familiar"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
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
    observacoes = Column(String(255))

    paciente = relationship("Paciente", back_populates="familiares")


class HabitosDeVida(Base):
    __tablename__ = "habitos_de_vida"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    # Tabagismo
    tabagismo = Column(String(20), default='nao')  # 'nao', 'sim', 'ex'
    tabagismo_carga = Column(String(50))
    tabagismo_tempo_anos = Column(String(50))
    
    # Etilismo
    etilismo = Column(String(20), default='nao')  # 'nao', 'sim', 'ex'
    etilismo_tempo_anos = Column(String(50))
    
    # Atividade física
    atividade_fisica = Column(String(20), default='nao')  # 'nao', 'sim'
    tipo_atividade = Column(String(100))
    tempo_atividade_semanal_min = Column(String(50))

    paciente = relationship("Paciente", back_populates="habitos_vida")


class Paridade(Base):
    __tablename__ = "paridade"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    # Paridade
    gesta = Column(String(10))
    para = Column(String(10))
    aborto = Column(String(10))
    teve_filhos = Column(Boolean, default=False)
    idade_primeiro_filho = Column(String(10))
    
    # Amamentação
    amamentou = Column(Boolean, default=False)
    tempo_amamentacao_meses = Column(String(10))
    
    # Menstruação
    menarca_idade = Column(String(10))
    menopausa = Column(String(20), default='nao')  # 'nao', 'sim', 'cirurgica'
    idade_menopausa = Column(String(10))
    
    # Terapia hormonal
    uso_trh = Column(Boolean, default=False)
    tempo_uso_trh = Column(String(10))
    uso_aco = Column(Boolean, default=False)
    tempo_uso_aco = Column(String(10))

    paciente = relationship("Paciente", back_populates="paridade")


class HistoriaDoencaAtual(Base):
    __tablename__ = "historia_doenca_atual"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    # Sintomas e diagnóstico
    sinal_sintoma_principal = Column(String(255))
    outro_sinal_sintoma = Column(String(255))
    data_sintomas = Column(Date)
    idade_diagnostico = Column(Integer)
    ecog = Column(String(10))
    lado_acometido = Column(String(20))
    tamanho_tumoral_clinico = Column(String(50))
    linfonodos_palpaveis = Column(String(20), default='nao')
    estadiamento_clinico = Column(String(50))
    metastase_distancia = Column(Boolean, default=False)
    locais_metastase = Column(String(255))

    paciente = relationship("Paciente", back_populates="historia_doenca")

class ModelosPreditores(Base):
    __tablename__ = "modelos_preditores"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    score_tyrer_cuzick = Column(Numeric(5, 2))
    score_canrisk = Column(Numeric(5, 2))
    score_gail = Column(Numeric(5, 2))

    paciente = relationship("Paciente", back_populates="modelos_preditores")


# Modelo Histologia removido conforme solicitado pelo usuário


# Modelos para estruturas complexas do tratamento
class CirurgiaMama(Base):
    __tablename__ = "cirurgia_mama"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data = Column(Date)
    tecnica = Column(String(100))
    tipo_histologico = Column(String(100))
    subtipo_histologico = Column(String(100))
    tamanho_tumor = Column(Numeric(5, 2))
    grau_histologico = Column(String(50))
    margens = Column(String(50))  # 'livres', 'comprometidas'
    margens_comprometidas_dimensao = Column(Numeric(5, 2))
    linfonodos_excisados = Column(Integer)
    linfonodos_comprometidos = Column(Integer)
    invasao_extranodal = Column(Boolean, default=False)
    invasao_extranodal_dimensao = Column(Numeric(5, 2))
    imunohistoquimica = Column(Boolean, default=False)
    imunohistoquimica_resultado = Column(String(500))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="cirurgias_mama")

class CirurgiaAxila(Base):
    __tablename__ = "cirurgia_axila"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data = Column(Date)
    tecnica = Column(String(100))
    tipo_histologico = Column(String(100))
    subtipo_histologico = Column(String(100))
    n_linfonodos_excisados = Column(Integer)
    n_linfonodos_comprometidos = Column(Integer)
    invasao_extranodal = Column(Boolean, default=False)
    invasao_extranodal_dimensao = Column(Numeric(5, 2))
    imunohistoquimica = Column(Boolean, default=False)
    imunohistoquimica_resultado = Column(String(500))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="cirurgias_axila")

class Reconstrucao(Base):
    __tablename__ = "reconstrucao"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data = Column(Date)
    tecnica = Column(String(100))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="reconstrucoes")

class Quimioterapia(Base):
    __tablename__ = "quimioterapia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tipo = Column(String(50))  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(String(255))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="quimioterapias")

class Radioterapia(Base):
    __tablename__ = "radioterapia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tipo = Column(String(50))  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(String(255))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="radioterapias")

class Endocrinoterapia(Base):
    __tablename__ = "endocrinoterapia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tipo = Column(String(50))  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(String(255))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="endocrinoterapias")

class Imunoterapia(Base):
    __tablename__ = "imunoterapia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    tipo = Column(String(50))  # 'neoadjuvante', 'adjuvante', 'paliativa'
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(String(255))
    intercorrencias = Column(String(500))

    paciente = relationship("Paciente", back_populates="imunoterapias")

class Imunohistoquimica(Base):
    __tablename__ = "imunohistoquimica"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    marcador = Column(String(100))
    resultado = Column(String(100))
    percentual = Column(String(50))

    paciente = relationship("Paciente", back_populates="imunohistoquimicas")

class CoreBiopsy(Base):
    __tablename__ = "core_biopsy"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    realizada = Column(Boolean, default=False)
    data = Column(Date)
    especime = Column(String(100))
    tecnica = Column(String(100))
    tipo_lesao = Column(String(100))
    anatomopatologico = Column(String(100))
    tipo_histologico = Column(String(100))

    paciente = relationship("Paciente", back_populates="core_biopsies")

class Mamotomia(Base):
    __tablename__ = "mamotomia"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    realizada = Column(Boolean, default=False)
    data = Column(Date)
    especime = Column(String(100))
    tecnica = Column(String(100))
    tipo_lesao = Column(String(100))
    anatomopatologico = Column(String(100))
    tipo_histologico = Column(String(100))

    paciente = relationship("Paciente", back_populates="mamotomias")

class Paaf(Base):
    __tablename__ = "paaf"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    realizada = Column(Boolean, default=False)
    data = Column(Date)
    especime = Column(String(100))
    tecnica = Column(String(100))
    achados = Column(String(500))

    paciente = relationship("Paciente", back_populates="paafs")


class Desfecho(Base):
    __tablename__ = "desfecho"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    
    # Status vital
    status_vital = Column(String(50))  # 'vivo', 'morto'
    data_morte = Column(Date)
    causa_morte = Column(String(255))
    
    # Recidivas
    recidiva_local = Column(Boolean, default=False)
    data_recidiva_local = Column(Date)
    cirurgia_recidiva_local = Column(String(255))
    recidiva_regional = Column(Boolean, default=False)
    data_recidiva_regional = Column(Date)
    cirurgia_recidiva_regional = Column(String(255))

    paciente = relationship("Paciente", back_populates="desfecho")

class Metastase(Base):
    __tablename__ = "metastase"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    local = Column(String(255))
    data_diagnostico = Column(Date)
    tratamento = Column(String(500))
    observacoes = Column(String(500))

    paciente = relationship("Paciente", back_populates="metastases")


class TemposDiagnostico(Base):
    __tablename__ = "tempos_diagnostico"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data_primeira_consulta = Column(Date)
    data_diagnostico = Column(Date)
    data_inicio_tratamento = Column(Date)
    data_cirurgia = Column(Date)

    paciente = relationship("Paciente", back_populates="tempos_diagnostico")

class Evento(Base):
    __tablename__ = "evento"
    __table_args__ = {"schema": "masto"}
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("masto.paciente.paciente_id", ondelete="CASCADE"))
    data = Column(Date)
    descricao = Column(String(255))
    observacoes = Column(String(500))

    paciente = relationship("Paciente", back_populates="eventos")
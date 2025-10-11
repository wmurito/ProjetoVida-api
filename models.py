from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, DateTime, JSON, Text, CHAR
from sqlalchemy.orm import relationship
from database import Base
import datetime

# =======================================================================
# 1. PACIENTE (Tabela Principal)
# =======================================================================
class Paciente(Base):
    __tablename__ = "paciente"
    
    # CHAVE PRIMÁRIA
    id_paciente = Column(Integer, primary_key=True, index=True)

    # DADOS PESSOAIS E ENDEREÇO
    nome_completo = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    genero = Column(String(50))
    estado_civil = Column(String(50))
    cor_etnia = Column(String(50))
    escolaridade = Column(String(100))
    renda_familiar = Column(String(100))
    naturalidade = Column(String(100))
    cep = Column(String(10))
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(CHAR(2))
    telefone = Column(String(20))
    
    # DADOS FÍSICOS
    altura = Column(Numeric(5, 2))
    peso = Column(Numeric(5, 2))
    imc = Column(Numeric(5, 2))
    idade = Column(Integer)

    # HISTÓRIA PATOLÓGICA (HP)
    hp_has = Column(Boolean, default=False)
    hp_diabetes = Column(Boolean, default=False)
    hp_hipertensao = Column(Boolean, default=False)
    hp_hipotireoidismo = Column(Boolean, default=False)
    hp_ansiedade = Column(Boolean, default=False)
    hp_depressao = Column(Boolean, default=False)
    hp_doenca_cardiaca = Column(Boolean, default=False)
    hp_doenca_renal = Column(Boolean, default=False)
    hp_doenca_pulmonar = Column(Boolean, default=False)
    hp_doenca_figado = Column(Boolean, default=False)
    hp_avc = Column(Boolean, default=False)
    hp_outra = Column(Text)
    hp_neoplasia_previa = Column(Boolean, default=False)
    hp_qual_neoplasia = Column(Text)
    hp_idade_diagnostico_neoplasia = Column(String(50))
    hp_biopsia_mamaria_previa = Column(Boolean, default=False)
    hp_resultado_biopsia = Column(Text)

    # HISTÓRIA FAMILIAR (HF)
    hf_cancer_familia = Column(Boolean, default=False)
    hf_observacoes = Column(Text)

    # HÁBITOS DE VIDA (HV)
    hv_tabagismo = Column(String(10))
    hv_tabagismo_carga = Column(String(50))
    hv_tabagismo_tempo_anos = Column(String(50))
    hv_etilismo = Column(String(10))
    hv_etilismo_tempo_anos = Column(String(50))
    hv_etilismo_dose_diaria = Column(String(50))
    hv_atividade_fisica = Column(String(10))
    hv_tipo_atividade = Column(String(100))
    hv_tempo_atividade_semanal_min = Column(String(50))
    
    # PARIDADE (P)
    p_gesta = Column(String(50))
    p_para = Column(String(50))
    p_aborto = Column(String(50))
    p_teve_filhos = Column(Boolean, default=False)
    p_idade_primeiro_filho = Column(String(50))
    p_amamentou = Column(Boolean, default=False)
    p_tempo_amamentacao_meses = Column(String(50))
    p_menarca_idade = Column(String(50))
    p_menopausa = Column(String(10))
    p_idade_menopausa = Column(String(50))
    p_uso_trh = Column(Boolean, default=False)
    p_tempo_uso_trh = Column(String(50))
    p_tipo_terapia = Column(String(100)) # CORRIGIDO: Campo faltante no ORM original
    p_uso_aco = Column(Boolean, default=False)
    p_tempo_uso_aco = Column(String(50))

    # HISTÓRIA DA DOENÇA (HD)
    hd_sinal_sintoma_principal = Column(Text, nullable=False)
    hd_outro_sinal_sintoma = Column(Text)
    hd_data_sintomas = Column(Date, nullable=False)
    hd_idade_diagnostico = Column(Integer, nullable=False)
    hd_ecog = Column(String(50))
    hd_lado_acometido = Column(String(50), nullable=False)
    hd_tamanho_tumoral_clinico = Column(Numeric(5, 2))
    hd_linfonodos_palpaveis = Column(String(10))
    hd_estadiamento_clinico = Column(String(50))
    hd_metastase_distancia = Column(Boolean, default=False)
    hd_locais_metastase = Column(Text)

    # MODELOS PREDITORES (MP)
    mp_score_tyrer_cuzick = Column(String(50))
    mp_score_canrisk = Column(String(50))
    mp_score_gail = Column(String(50))
    
    # Relacionamentos
    familiares = relationship("PacienteFamiliar", back_populates="paciente", cascade="all, delete-orphan")
    tratamento = relationship("Tratamento", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    desfecho = relationship("Desfecho", back_populates="paciente", cascade="all, delete-orphan", uselist=False)
    historico = relationship("PacienteHistorico", back_populates="paciente", cascade="all, delete-orphan")


# =======================================================================
# 2. PACIENTE_FAMILIARES (1:N)
# CORRIGIDO: Detalhamento para câncer familiar
# =======================================================================
class PacienteFamiliar(Base):
    __tablename__ = "paciente_familiares"
    
    id_familiar = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    nome = Column(String(255))
    parentesco = Column(String(100))

    # CAMPOS DETALHADOS (CORRIGIDO)
    genero = Column(String(50))
    tem_cancer_mama = Column(Boolean, default=False)
    idade_cancer_mama = Column(String(50))
    bilateral = Column(Boolean, default=False)
    idade_segunda_mama = Column(String(50))
    tem_cancer_ovario = Column(Boolean, default=False)
    idade_cancer_ovario = Column(String(50))
    gene_brca = Column(String(50))
    tipo_cancer_outros = Column(Text) # Substitui o antigo tipo_cancer
    
    paciente = relationship("Paciente", back_populates="familiares")


# =======================================================================
# 3. TRATAMENTO (1:1)
# CORRIGIDO: Prefixos de Endócrino/Imuno e Campos de Biópsia
# =======================================================================
class Tratamento(Base):
    __tablename__ = "tratamento"
    
    id_tratamento = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False, unique=True)
    
    # CIRURGIA
    t_cirurgia_contexto_cirurgico = Column(String(50))
    
    # QUIMIOTERAPIA NEADJUVANTE
    qt_neoadj_data_inicio = Column(Date)
    qt_neoadj_data_termino = Column(Date)
    qt_neoadj_esquema = Column(Text)
    qt_neoadj_intercorrencias = Column(Text)
    
    # QUIMIOTERAPIA ADJUVANTE
    qt_adj_data_inicio = Column(Date)
    qt_adj_data_termino = Column(Date)
    qt_adj_esquema = Column(Text)
    qt_adj_intercorrencias = Column(Text)
    
    # RADIOTERAPIA NEADJUVANTE
    rt_neoadj_data_inicio = Column(Date)
    rt_neoadj_data_termino = Column(Date)
    rt_neoadj_esquema = Column(Text)
    rt_neoadj_intercorrencias = Column(Text)
    
    # RADIOTERAPIA ADJUVANTE
    rt_adj_data_inicio = Column(Date)
    rt_adj_data_termino = Column(Date)
    rt_adj_esquema = Column(Text)
    rt_adj_intercorrencias = Column(Text)
    
    # ENDOCRINOTERAPIA NEADJUVANTE (CORRIGIDO prefixo de et_ para endo_)
    endo_neoadj_data_inicio = Column(Date)
    endo_neoadj_data_termino = Column(Date)
    endo_neoadj_esquema = Column(Text)
    endo_neoadj_intercorrencias = Column(Text)
    
    # ENDOCRINOTERAPIA ADJUVANTE (CORRIGIDO prefixo de et_ para endo_)
    endo_adj_data_inicio = Column(Date)
    endo_adj_data_termino = Column(Date)
    endo_adj_esquema = Column(Text)
    endo_adj_intercorrencias = Column(Text)
    
    # IMUNOTERAPIA NEADJUVANTE (CORRIGIDO prefixo de it_ para imuno_)
    imuno_neoadj_data_inicio = Column(Date)
    imuno_neoadj_data_termino = Column(Date)
    imuno_neoadj_esquema = Column(Text)
    imuno_neoadj_intercorrencias = Column(Text)
    
    # IMUNOTERAPIA ADJUVANTE (CORRIGIDO prefixo de it_ para imuno_)
    imuno_adj_data_inicio = Column(Date)
    imuno_adj_data_termino = Column(Date)
    imuno_adj_esquema = Column(Text)
    imuno_adj_intercorrencias = Column(Text)

    # CORE BIOPSY
    t_core_biopsy_realizada = Column(Boolean, default=False)
    t_core_biopsy_data = Column(Date)
    t_core_biopsy_especime = Column(String(255))
    t_core_biopsy_tecnica = Column(String(255))
    t_core_biopsy_tipo_lesao = Column(String(255))
    t_core_biopsy_anatomopatologico = Column(String(255))
    t_core_biopsy_tipo_histologico = Column(String(255))
    
    # MAMOTOMIA
    t_mamotomia_realizada = Column(Boolean, default=False)
    t_mamotomia_data = Column(Date)
    t_mamotomia_especime = Column(String(255))
    t_mamotomia_tecnica = Column(String(255))
    t_mamotomia_tipo_lesao = Column(String(255))
    t_mamotomia_anatomopatologico = Column(String(255))
    t_mamotomia_tipo_histologico = Column(String(255))
    
    # PAAF
    t_paaf_realizada = Column(Boolean, default=False)
    t_paaf_data = Column(Date)
    t_paaf_especime = Column(String(255))
    t_paaf_tecnica = Column(String(255))
    t_paaf_achados = Column(Text)
    
    paciente = relationship("Paciente", back_populates="tratamento")
    
    # Relacionamentos 1:N (Simplificados para a melhor prática com 1 Tabela de Cirurgia)
    cirurgias = relationship("TratamentoCirurgia", back_populates="tratamento", cascade="all, delete-orphan")
    quimio_paliativa = relationship("PalliativoQuimioterapia", back_populates="tratamento", cascade="all, delete-orphan")
    radio_paliativa = relationship("PalliativoRadioterapia", back_populates="tratamento", cascade="all, delete-orphan")
    endo_paliativa = relationship("PalliativoEndocrinoterapia", back_populates="tratamento", cascade="all, delete-orphan")
    imuno_paliativa = relationship("PalliativoImunoterapia", back_populates="tratamento", cascade="all, delete-orphan")
    imunohistoquimicas = relationship("Imunohistoquimicas", back_populates="tratamento", cascade="all, delete-orphan")


# =======================================================================
# 4. DESFECHO (1:1)
# CORRIGIDO: Adicionado flag 'morte'
# =======================================================================
class Desfecho(Base):
    __tablename__ = "desfecho"
    
    id_desfecho = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False, unique=True)
    
    # STATUS VITAL
    status_vital = Column(String(50))
    morte = Column(Boolean, default=False) # CORRIGIDO: Campo faltante no ORM
    data_morte = Column(Date)
    causa_morte = Column(Text)
    
    # RECIDIVA / METÁSTASE
    recidiva_local = Column(Boolean, default=False)
    data_recidiva_local = Column(Date)
    cirurgia_recidiva_local = Column(Text)
    recidiva_regional = Column(Boolean, default=False)
    data_recidiva_regional = Column(Date)
    cirurgia_recidiva_regional = Column(Text)
    metastase_ocorreu = Column(Boolean, default=False)

    # TEMPOS DE DIAGNÓSTICO (TD)
    td_data_primeira_consulta = Column(Date)
    td_data_diagnostico = Column(Date)
    td_data_inicio_tratamento = Column(Date)
    td_data_cirurgia = Column(Date)
    
    paciente = relationship("Paciente", back_populates="desfecho")
    
    # Relacionamentos 1:N
    metastases = relationship("DesfechoMetastases", back_populates="desfecho", cascade="all, delete-orphan")
    eventos = relationship("DesfechoEventos", back_populates="desfecho", cascade="all, delete-orphan")


# =======================================================================
# TABELAS DE RELACIONAMENTO 1:N com TRATAMENTO
# (Classes de cirurgia unificadas)
# =======================================================================
class TratamentoCirurgia(Base):
    __tablename__ = "tratamento_cirurgia"
    
    id_cirurgia = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    tipo_procedimento = Column(String(50)) # mama, axila, reconstrucao
    procedimento = Column(String(100))
    data_cirurgia = Column(Date)
    
    tratamento = relationship("Tratamento", back_populates="cirurgias")


class PalliativoQuimioterapia(Base):
    __tablename__ = "palliativo_quimioterapia"
    
    id_quimio_paliativa = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(Text)
    intercorrencias = Column(Text)
    
    tratamento = relationship("Tratamento", back_populates="quimio_paliativa")


class PalliativoRadioterapia(Base):
    __tablename__ = "palliativo_radioterapia"
    
    id_radio_paliativa = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    data_inicio = Column(Date)
    data_termino = Column(Date)
    sitio = Column(String(255)) # CORRIGIDO: Campo 'sitio' faltante no ORM original
    esquema = Column(Text)
    intercorrencias = Column(Text)
    
    tratamento = relationship("Tratamento", back_populates="radio_paliativa")


class PalliativoEndocrinoterapia(Base):
    __tablename__ = "palliativo_endocrinoterapia"
    
    id_endo_paliativa = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(Text)
    intercorrencias = Column(Text)
    
    tratamento = relationship("Tratamento", back_populates="endo_paliativa")


class PalliativoImunoterapia(Base):
    __tablename__ = "palliativo_imunoterapia"
    
    id_imuno_paliativa = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    data_inicio = Column(Date)
    data_termino = Column(Date)
    esquema = Column(Text)
    intercorrencias = Column(Text)
    
    tratamento = relationship("Tratamento", back_populates="imuno_paliativa")


class Imunohistoquimicas(Base):
    __tablename__ = "imunohistoquimicas"
    
    id_imunohistoquimica = Column(Integer, primary_key=True, index=True)
    id_tratamento = Column(Integer, ForeignKey("tratamento.id_tratamento", ondelete="CASCADE"), nullable=False)
    
    # CAMPOS COMPLETOS (CORRIGIDO)
    tipo = Column(String(50))
    especime = Column(String(255))
    data_realizacao = Column(Date)
    re = Column(String(50))
    rp = Column(String(50))
    ki67 = Column(String(50))
    her2 = Column(String(50))
    fish = Column(String(50))
    outras_informacoes = Column(Text)

    tratamento = relationship("Tratamento", back_populates="imunohistoquimicas")


# =======================================================================
# TABELAS DE RELACIONAMENTO 1:N com DESFECHO
# =======================================================================
class DesfechoMetastases(Base):
    __tablename__ = "desfecho_metastases"
    
    id_desfecho_metastase = Column(Integer, primary_key=True, index=True)
    id_desfecho = Column(Integer, ForeignKey("desfecho.id_desfecho", ondelete="CASCADE"), nullable=False)
    local = Column(String(255))
    
    desfecho = relationship("Desfecho", back_populates="metastases")


class DesfechoEventos(Base):
    __tablename__ = "desfecho_eventos"
    
    id_evento = Column(Integer, primary_key=True, index=True)
    id_desfecho = Column(Integer, ForeignKey("desfecho.id_desfecho", ondelete="CASCADE"), nullable=False)
    data = Column(Date)
    titulo = Column(String(255))
    descricao = Column(Text)
    
    desfecho = relationship("Desfecho", back_populates="eventos")


# =======================================================================
# TABELA DE HISTÓRICO (Auditoria)
# =======================================================================
class PacienteHistorico(Base):
    __tablename__ = "paciente_historico"
    
    id = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    data_modificacao = Column(DateTime, default=datetime.datetime.utcnow)
    dados_anteriores = Column(JSON)
    
    paciente = relationship("Paciente", back_populates="historico")
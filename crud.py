from sqlalchemy.orm import Session
from sqlalchemy import text
import models, schemas
from typing import Optional
import datetime


# Função para criar ou atualizar dados relacionados
def create_or_update_related_data(db: Session, paciente: schemas.PacienteCreate, paciente_id: int):
    # História Patológica
    if paciente.historia_patologica:
        existing = db.query(models.HistoriaPatologica).filter(
            models.HistoriaPatologica.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.historia_patologica.dict().items():
                setattr(existing, key, value)
        else:
            db_historia_patologica = models.HistoriaPatologica(
                **paciente.historia_patologica.dict(),
                paciente_id=paciente_id
            )
            db.add(db_historia_patologica)
    
    # História Familiar
    if paciente.historia_familiar:
        existing = db.query(models.HistoriaFamiliar).filter(
            models.HistoriaFamiliar.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.historia_familiar.dict().items():
                setattr(existing, key, value)
        else:
            db_historia_familiar = models.HistoriaFamiliar(
                **paciente.historia_familiar.dict(),
                paciente_id=paciente_id
            )
            db.add(db_historia_familiar)
    
    # Familiares (lista)
    if paciente.familiares:
        # Remover familiares existentes
        db.query(models.Familiar).filter(models.Familiar.paciente_id == paciente_id).delete()
        
        # Adicionar novos familiares
        for familiar_data in paciente.familiares:
            db_familiar = models.Familiar(
                **familiar_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_familiar)
    
    # Hábitos de Vida
    if paciente.habitos_vida:
        existing = db.query(models.HabitosDeVida).filter(
            models.HabitosDeVida.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.habitos_vida.dict().items():
                setattr(existing, key, value)
        else:
            db_habitos_vida = models.HabitosDeVida(
                **paciente.habitos_vida.dict(),
                paciente_id=paciente_id
            )
            db.add(db_habitos_vida)
    
    # Paridade
    if paciente.paridade:
        existing = db.query(models.Paridade).filter(
            models.Paridade.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.paridade.dict().items():
                setattr(existing, key, value)
        else:
            db_paridade = models.Paridade(
                **paciente.paridade.dict(),
                paciente_id=paciente_id
            )
            db.add(db_paridade)
    
    # História da Doença
    if paciente.historia_doenca:
        existing = db.query(models.HistoriaDoencaAtual).filter(
            models.HistoriaDoencaAtual.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.historia_doenca.dict().items():
                setattr(existing, key, value)
        else:
            db_historia_doenca = models.HistoriaDoencaAtual(
                **paciente.historia_doenca.dict(),
                paciente_id=paciente_id
            )
            db.add(db_historia_doenca)
    
    # Modelos Preditores
    if paciente.modelos_preditores:
        existing = db.query(models.ModelosPreditores).filter(
            models.ModelosPreditores.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.modelos_preditores.dict().items():
                setattr(existing, key, value)
        else:
            db_modelos_preditores = models.ModelosPreditores(
                **paciente.modelos_preditores.dict(),
                paciente_id=paciente_id
            )
            db.add(db_modelos_preditores)
    
    # Cirurgias Mama (lista)
    if paciente.cirurgias_mama:
        db.query(models.CirurgiaMama).filter(models.CirurgiaMama.paciente_id == paciente_id).delete()
        for cirurgia_data in paciente.cirurgias_mama:
            db_cirurgia = models.CirurgiaMama(
                **cirurgia_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_cirurgia)
    
    # Cirurgias Axila (lista)
    if paciente.cirurgias_axila:
        db.query(models.CirurgiaAxila).filter(models.CirurgiaAxila.paciente_id == paciente_id).delete()
        for cirurgia_data in paciente.cirurgias_axila:
            db_cirurgia = models.CirurgiaAxila(
                **cirurgia_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_cirurgia)
    
    # Reconstruções (lista)
    if paciente.reconstrucoes:
        db.query(models.Reconstrucao).filter(models.Reconstrucao.paciente_id == paciente_id).delete()
        for reconstrucao_data in paciente.reconstrucoes:
            db_reconstrucao = models.Reconstrucao(
                **reconstrucao_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_reconstrucao)
    
    # Quimioterapias (lista)
    if paciente.quimioterapias:
        db.query(models.Quimioterapia).filter(models.Quimioterapia.paciente_id == paciente_id).delete()
        for quimio_data in paciente.quimioterapias:
            db_quimio = models.Quimioterapia(
                **quimio_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_quimio)
    
    # Radioterapias (lista)
    if paciente.radioterapias:
        db.query(models.Radioterapia).filter(models.Radioterapia.paciente_id == paciente_id).delete()
        for radio_data in paciente.radioterapias:
            db_radio = models.Radioterapia(
                **radio_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_radio)
    
    # Endocrinoterapias (lista)
    if paciente.endocrinoterapias:
        db.query(models.Endocrinoterapia).filter(models.Endocrinoterapia.paciente_id == paciente_id).delete()
        for endo_data in paciente.endocrinoterapias:
            db_endo = models.Endocrinoterapia(
                **endo_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_endo)
    
    # Imunoterapias (lista)
    if paciente.imunoterapias:
        db.query(models.Imunoterapia).filter(models.Imunoterapia.paciente_id == paciente_id).delete()
        for imuno_data in paciente.imunoterapias:
            db_imuno = models.Imunoterapia(
                **imuno_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_imuno)
    
    # Imunohistoquímicas (lista)
    if paciente.imunohistoquimicas:
        db.query(models.Imunohistoquimica).filter(models.Imunohistoquimica.paciente_id == paciente_id).delete()
        for imuno_data in paciente.imunohistoquimicas:
            db_imuno = models.Imunohistoquimica(
                **imuno_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_imuno)
    
    # Core Biopsies (lista)
    if paciente.core_biopsies:
        db.query(models.CoreBiopsy).filter(models.CoreBiopsy.paciente_id == paciente_id).delete()
        for biopsy_data in paciente.core_biopsies:
            db_biopsy = models.CoreBiopsy(
                **biopsy_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_biopsy)
    
    # Mamotomias (lista)
    if paciente.mamotomias:
        db.query(models.Mamotomia).filter(models.Mamotomia.paciente_id == paciente_id).delete()
        for mamotomia_data in paciente.mamotomias:
            db_mamotomia = models.Mamotomia(
                **mamotomia_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_mamotomia)
    
    # PAAFs (lista)
    if paciente.paafs:
        db.query(models.Paaf).filter(models.Paaf.paciente_id == paciente_id).delete()
        for paaf_data in paciente.paafs:
            db_paaf = models.Paaf(
                **paaf_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_paaf)
    
    # Desfecho
    if paciente.desfecho:
        existing = db.query(models.Desfecho).filter(
            models.Desfecho.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.desfecho.dict().items():
                setattr(existing, key, value)
        else:
            db_desfecho = models.Desfecho(
                **paciente.desfecho.dict(),
                paciente_id=paciente_id
            )
            db.add(db_desfecho)
    
    # Metástases (lista)
    if paciente.metastases:
        db.query(models.Metastase).filter(models.Metastase.paciente_id == paciente_id).delete()
        for metastase_data in paciente.metastases:
            db_metastase = models.Metastase(
                **metastase_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_metastase)
    
    # Tempos Diagnóstico
    if paciente.tempos_diagnostico:
        existing = db.query(models.TemposDiagnostico).filter(
            models.TemposDiagnostico.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.tempos_diagnostico.dict().items():
                setattr(existing, key, value)
        else:
            db_tempos_diagnostico = models.TemposDiagnostico(
                **paciente.tempos_diagnostico.dict(),
                paciente_id=paciente_id
            )
            db.add(db_tempos_diagnostico)
    
    # Eventos (lista)
    if paciente.eventos:
        db.query(models.Evento).filter(models.Evento.paciente_id == paciente_id).delete()
        for evento_data in paciente.eventos:
            db_evento = models.Evento(
                **evento_data.dict(),
                paciente_id=paciente_id
            )
            db.add(db_evento)
    
    db.commit()


# ✅ Função para criar paciente e dados relacionados
def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    db_paciente = models.Paciente(**paciente.dict(exclude={
        "historia_patologica", "historia_familiar", "familiares", "habitos_vida",
        "paridade", "historia_doenca", "modelos_preditores",
        "cirurgias_mama", "cirurgias_axila", "reconstrucoes",
        "quimioterapias", "radioterapias", "endocrinoterapias", "imunoterapias",
        "imunohistoquimicas", "core_biopsies", "mamotomias", "paafs",
        "desfecho", "metastases", "tempos_diagnostico", "eventos"
    }))

    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)

    # Dados relacionados
    create_or_update_related_data(db, paciente, db_paciente.paciente_id)

    return get_paciente(db, db_paciente.paciente_id)


# ✅ Obter paciente específico
def get_paciente(db: Session, paciente_id: int):
    return db.query(models.Paciente).filter(models.Paciente.paciente_id == paciente_id).first()


# ✅ Listar pacientes
def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Paciente).offset(skip).limit(limit).all()

def get_paciente_detalhes(db: Session, paciente_id: int):
    # Buscar paciente com todos os relacionamentos usando SQLAlchemy ORM
    paciente = db.query(models.Paciente).filter(models.Paciente.paciente_id == paciente_id).first()
    if not paciente:
        return None
    
    # Buscar todos os dados relacionados
    historia_patologica = db.query(models.HistoriaPatologica).filter(
        models.HistoriaPatologica.paciente_id == paciente_id
    ).first()
    
    historia_familiar = db.query(models.HistoriaFamiliar).filter(
        models.HistoriaFamiliar.paciente_id == paciente_id
    ).first()
    
    familiares = db.query(models.Familiar).filter(
        models.Familiar.paciente_id == paciente_id
    ).all()
    
    habitos_vida = db.query(models.HabitosDeVida).filter(
        models.HabitosDeVida.paciente_id == paciente_id
    ).first()
    
    paridade = db.query(models.Paridade).filter(
        models.Paridade.paciente_id == paciente_id
    ).first()
    
    historia_doenca = db.query(models.HistoriaDoencaAtual).filter(
        models.HistoriaDoencaAtual.paciente_id == paciente_id
    ).first()
    
    modelos_preditores = db.query(models.ModelosPreditores).filter(
        models.ModelosPreditores.paciente_id == paciente_id
    ).first()
    
    # Tratamento - listas
    cirurgias_mama = db.query(models.CirurgiaMama).filter(
        models.CirurgiaMama.paciente_id == paciente_id
    ).all()
    
    cirurgias_axila = db.query(models.CirurgiaAxila).filter(
        models.CirurgiaAxila.paciente_id == paciente_id
    ).all()
    
    reconstrucoes = db.query(models.Reconstrucao).filter(
        models.Reconstrucao.paciente_id == paciente_id
    ).all()
    
    quimioterapias = db.query(models.Quimioterapia).filter(
        models.Quimioterapia.paciente_id == paciente_id
    ).all()
    
    radioterapias = db.query(models.Radioterapia).filter(
        models.Radioterapia.paciente_id == paciente_id
    ).all()
    
    endocrinoterapias = db.query(models.Endocrinoterapia).filter(
        models.Endocrinoterapia.paciente_id == paciente_id
    ).all()
    
    imunoterapias = db.query(models.Imunoterapia).filter(
        models.Imunoterapia.paciente_id == paciente_id
    ).all()
    
    imunohistoquimicas = db.query(models.Imunohistoquimica).filter(
        models.Imunohistoquimica.paciente_id == paciente_id
    ).all()
    
    core_biopsies = db.query(models.CoreBiopsy).filter(
        models.CoreBiopsy.paciente_id == paciente_id
    ).all()
    
    mamotomias = db.query(models.Mamotomia).filter(
        models.Mamotomia.paciente_id == paciente_id
    ).all()
    
    paafs = db.query(models.Paaf).filter(
        models.Paaf.paciente_id == paciente_id
    ).all()
    
    desfecho = db.query(models.Desfecho).filter(
        models.Desfecho.paciente_id == paciente_id
    ).first()
    
    metastases = db.query(models.Metastase).filter(
        models.Metastase.paciente_id == paciente_id
    ).all()
    
    tempos_diagnostico = db.query(models.TemposDiagnostico).filter(
        models.TemposDiagnostico.paciente_id == paciente_id
    ).first()
    
    eventos = db.query(models.Evento).filter(
        models.Evento.paciente_id == paciente_id
    ).all()
    
    # Montar resultado
    result = {
        "paciente": paciente,
        "historia_patologica": historia_patologica,
        "historia_familiar": historia_familiar,
        "familiares": familiares,
        "habitos_vida": habitos_vida,
        "paridade": paridade,
        "historia_doenca": historia_doenca,
        "modelos_preditores": modelos_preditores,
        "cirurgias_mama": cirurgias_mama,
        "cirurgias_axila": cirurgias_axila,
        "reconstrucoes": reconstrucoes,
        "quimioterapias": quimioterapias,
        "radioterapias": radioterapias,
        "endocrinoterapias": endocrinoterapias,
        "imunoterapias": imunoterapias,
        "imunohistoquimicas": imunohistoquimicas,
        "core_biopsies": core_biopsies,
        "mamotomias": mamotomias,
        "paafs": paafs,
        "desfecho": desfecho,
        "metastases": metastases,
        "tempos_diagnostico": tempos_diagnostico,
        "eventos": eventos
    }
    
    return result

# ✅ Atualizar paciente + histórico
def update_paciente(db: Session, paciente_id: int, paciente: schemas.PacienteCreate):
    db_paciente = get_paciente(db, paciente_id)
    if not db_paciente:
        return None

    save_paciente_historico(db, db_paciente)

    for key, value in paciente.dict(exclude={
        "historia_patologica", "historia_familiar", "familiares", "habitos_vida",
        "paridade", "historia_doenca", "modelos_preditores",
        "cirurgias_mama", "cirurgias_axila", "reconstrucoes",
        "quimioterapias", "radioterapias", "endocrinoterapias", "imunoterapias",
        "imunohistoquimicas", "core_biopsies", "mamotomias", "paafs",
        "desfecho", "metastases", "tempos_diagnostico", "eventos"
    }).items():
        setattr(db_paciente, key, value)

    create_or_update_related_data(db, paciente, paciente_id)

    db.commit()
    db.refresh(db_paciente)
    return db_paciente


# ✅ Deletar paciente
def delete_paciente(db: Session, paciente_id: int):
    paciente = get_paciente(db, paciente_id)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente


# ✅ Salvar histórico completo
def save_paciente_historico(db: Session, paciente: models.Paciente):
    paciente_dict = {
        "paciente_id": paciente.paciente_id,
        "nome_completo": paciente.nome_completo,
        "idade": paciente.idade,
        "endereco": paciente.endereco,
        "cidade": paciente.cidade,
        "data_nascimento": str(paciente.data_nascimento) if paciente.data_nascimento else None,
        "telefone": paciente.telefone,
        "naturalidade": paciente.naturalidade,
        "altura": float(paciente.altura) if paciente.altura else None,
        "peso": float(paciente.peso) if paciente.peso else None,
        "imc": float(paciente.imc) if paciente.imc else None,
        "cor_etnia": paciente.cor_etnia,
        "escolaridade": paciente.escolaridade,
        "renda_familiar": paciente.renda_familiar,
    }

    # Dados relacionados
    paciente_dict["historia_patologica"] = [
        {
            "hipertensao": hp.hipertensao,
            "hipotireoidismo": hp.hipotireoidismo,
            "ansiedade": hp.ansiedade,
            "depressao": hp.depressao,
            "diabetes": hp.diabetes,
            "outros": hp.outros
        } for hp in paciente.historia_patologica
    ]

    paciente_dict["historia_familiar"] = [
        {
            "familia_cancer": hf.familia_cancer,
            "parentesco": hf.parentesco,
            "idade_diagnostico": hf.idade_diagnostico
        } for hf in paciente.historia_familiar
    ]

    paciente_dict["habitos_vida"] = [
        {
            "etilismo": hv.etilismo,
            "tabagismo": hv.tabagismo,
            "atividade_fisica": hv.atividade_fisica,
            "alimentacao": hv.alimentacao
        } for hv in paciente.habitos_vida
    ]

    paciente_dict["paridade"] = [
        {
            "menarca": p.menarca,
            "menopausa": p.menopausa,
            "idade_primeira_gestacao": p.idade_primeira_gestacao,
            "qtd_gestacoes": p.qtd_gestacoes
        } for p in paciente.paridade
    ]

    paciente_dict["historia_doenca"] = [
        {
            "data_diagnostico": str(hd.data_diagnostico) if hd.data_diagnostico else None,
            "localizacao": hd.localizacao,
            "estagio": hd.estagio,
            "subtipo": hd.subtipo
        } for hd in paciente.historia_doenca
    ]

    paciente_dict["histologia"] = [
        {
            "biopsia": h.biopsia,
            "grau_histologico": h.grau_histologico,
            "receptor_hormonal": h.receptor_hormonal
        } for h in paciente.histologia
    ]

    paciente_dict["tratamento"] = [
        {
            "cirurgia": t.cirurgia,
            "quimioterapia": t.quimioterapia,
            "radioterapia": t.radioterapia,
            "hormonoterapia": t.hormonoterapia
        } for t in paciente.tratamento
    ]

    paciente_dict["desfecho"] = [
        {
            "status_vital": d.status_vital,
            "data_obito": str(d.data_obito) if d.data_obito else None,
            "recidiva": d.recidiva
        } for d in paciente.desfecho
    ]

    paciente_dict["tempos_diagnostico"] = [
        {
            "tempo_inicio_sintomas_diagnostico": td.tempo_inicio_sintomas_diagnostico,
            "tempo_diagnostico_tratamento": td.tempo_diagnostico_tratamento
        } for td in paciente.tempos_diagnostico
    ]

    historico = models.PacienteHistorico(
        paciente_id=paciente.paciente_id,
        data_modificacao=datetime.datetime.utcnow(),
        dados_anteriores=paciente_dict
    )

    db.add(historico)
    db.flush()
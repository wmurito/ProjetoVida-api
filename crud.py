from sqlalchemy.orm import Session
from sqlalchemy import text
import models, schemas
from typing import Optional
import datetime


# Função para criar ou atualizar dados relacionados
def create_or_update_related_data(db: Session, paciente: schemas.PacienteCreate, paciente_id: int):
    # História Patológica
    if paciente.historia_patologica:
        # Verificar se já existe
        existing = db.query(models.HistoriaPatologica).filter(
            models.HistoriaPatologica.paciente_id == paciente_id
        ).first()
        
        if existing:
            # Atualizar
            for key, value in paciente.historia_patologica.dict().items():
                setattr(existing, key, value)
        else:
            # Criar novo
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
    
    # Histologia
    if paciente.histologia:
        existing = db.query(models.Histologia).filter(
            models.Histologia.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.histologia.dict().items():
                setattr(existing, key, value)
        else:
            db_histologia = models.Histologia(
                **paciente.histologia.dict(),
                paciente_id=paciente_id
            )
            db.add(db_histologia)
    
    # Tratamento
    if paciente.tratamento:
        existing = db.query(models.Tratamento).filter(
            models.Tratamento.paciente_id == paciente_id
        ).first()
        
        if existing:
            for key, value in paciente.tratamento.dict().items():
                setattr(existing, key, value)
        else:
            db_tratamento = models.Tratamento(
                **paciente.tratamento.dict(),
                paciente_id=paciente_id
            )
            db.add(db_tratamento)
    
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
    
    db.commit()


# ✅ Função para criar paciente e dados relacionados
def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    db_paciente = models.Paciente(**paciente.dict(exclude={
        "historia_patologica", "historia_familiar", "habitos_vida",
        "paridade", "historia_doenca", "histologia", "tratamento",
        "desfecho", "tempos_diagnostico"
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
    query = text("""
        SELECT 
            p.*,
            hp.*,
            hf.*,
            hv.*,
            pa.*,
            hda.*,
            hi.*,
            t.*,
            d.*,
            td.*
        FROM 
            masto.paciente p
        LEFT JOIN masto.historia_patologica hp ON hp.paciente_id = p.paciente_id
        LEFT JOIN masto.historia_familiar hf ON hf.paciente_id = p.paciente_id
        LEFT JOIN masto.habitos_de_vida hv ON hv.paciente_id = p.paciente_id
        LEFT JOIN masto.paridade pa ON pa.paciente_id = p.paciente_id
        LEFT JOIN masto.historia_doenca_atual hda ON hda.paciente_id = p.paciente_id
        LEFT JOIN masto.histologia hi ON hi.paciente_id = p.paciente_id
        LEFT JOIN masto.tratamento t ON t.paciente_id = p.paciente_id
        LEFT JOIN masto.desfecho d ON d.paciente_id = p.paciente_id
        LEFT JOIN masto.tempos_diagnostico td ON td.paciente_id = p.paciente_id
        WHERE p.paciente_id = :paciente_id
    """)
    result = db.execute(query, {"paciente_id": paciente_id}).mappings().first()
    return result

# ✅ Atualizar paciente + histórico
def update_paciente(db: Session, paciente_id: int, paciente: schemas.PacienteCreate):
    db_paciente = get_paciente(db, paciente_id)
    if not db_paciente:
        return None

    save_paciente_historico(db, db_paciente)

    for key, value in paciente.dict(exclude={
        "historia_patologica", "historia_familiar", "habitos_vida",
        "paridade", "historia_doenca", "histologia", "tratamento",
        "desfecho", "tempos_diagnostico"
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
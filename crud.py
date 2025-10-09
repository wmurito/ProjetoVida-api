from sqlalchemy.orm import Session
import models
import schemas
import datetime

def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    """Cria paciente com todos os dados relacionados"""
    
    # Criar paciente principal
    db_paciente = models.Paciente(**paciente.dict(exclude={
        "historia_patologica", "familiares", "habitos_vida", "paridade",
        "historia_doenca", "modelos_preditores", "tratamento", "desfecho", "tempos_diagnostico"
    }))
    db.add(db_paciente)
    db.flush()
    
    # História Patológica
    if paciente.historia_patologica:
        db_hist_pat = models.HistoriaPatologica(
            **paciente.historia_patologica.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_hist_pat)
    
    # Familiares
    if paciente.familiares:
        for familiar in paciente.familiares:
            db_familiar = models.Familiar(
                **familiar.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_familiar)
    
    # Hábitos de Vida
    if paciente.habitos_vida:
        db_habitos = models.HabitosVida(
            **paciente.habitos_vida.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_habitos)
    
    # Paridade
    if paciente.paridade:
        db_paridade = models.Paridade(
            **paciente.paridade.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_paridade)
    
    # História da Doença
    if paciente.historia_doenca:
        db_hist_doenca = models.HistoriaDoenca(
            **paciente.historia_doenca.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_hist_doenca)
    
    # Modelos Preditores
    if paciente.modelos_preditores:
        db_modelos = models.ModelosPreditores(
            **paciente.modelos_preditores.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_modelos)
    
    # Tratamento
    if paciente.tratamento:
        db_tratamento = models.Tratamento(
            **paciente.tratamento.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_tratamento)
    
    # Desfecho
    if paciente.desfecho:
        db_desfecho = models.Desfecho(
            **paciente.desfecho.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_desfecho)
    
    # Tempos Diagnóstico
    if paciente.tempos_diagnostico:
        db_tempos = models.TemposDiagnostico(
            **paciente.tempos_diagnostico.dict(),
            paciente_id=db_paciente.paciente_id
        )
        db.add(db_tempos)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def get_paciente(db: Session, paciente_id: int):
    """Busca paciente por ID"""
    return db.query(models.Paciente).filter(
        models.Paciente.paciente_id == paciente_id
    ).first()


def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    """Lista pacientes"""
    return db.query(models.Paciente).offset(skip).limit(limit).all()


def update_paciente(db: Session, paciente_id: int, paciente: schemas.PacienteCreate):
    """Atualiza paciente"""
    db_paciente = get_paciente(db, paciente_id)
    if not db_paciente:
        return None
    
    # Salvar histórico
    save_historico(db, db_paciente)
    
    # Atualizar dados principais
    for key, value in paciente.dict(exclude={
        "historia_patologica", "familiares", "habitos_vida", "paridade",
        "historia_doenca", "modelos_preditores", "tratamento", "desfecho", "tempos_diagnostico"
    }).items():
        setattr(db_paciente, key, value)
    
    # Atualizar relacionamentos
    update_relacionamentos(db, db_paciente, paciente)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def update_relacionamentos(db: Session, db_paciente, paciente: schemas.PacienteCreate):
    """Atualiza todos os relacionamentos"""
    
    # História Patológica
    if paciente.historia_patologica:
        if db_paciente.historia_patologica:
            for key, value in paciente.historia_patologica.dict().items():
                setattr(db_paciente.historia_patologica, key, value)
        else:
            db_hist = models.HistoriaPatologica(
                **paciente.historia_patologica.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_hist)
    
    # Familiares - remover antigos e adicionar novos
    if paciente.familiares is not None:
        for familiar in db_paciente.familiares:
            db.delete(familiar)
        for familiar_data in paciente.familiares:
            db_familiar = models.Familiar(
                **familiar_data.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_familiar)
    
    # Hábitos de Vida
    if paciente.habitos_vida:
        if db_paciente.habitos_vida:
            for key, value in paciente.habitos_vida.dict().items():
                setattr(db_paciente.habitos_vida, key, value)
        else:
            db_habitos = models.HabitosVida(
                **paciente.habitos_vida.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_habitos)
    
    # Paridade
    if paciente.paridade:
        if db_paciente.paridade:
            for key, value in paciente.paridade.dict().items():
                setattr(db_paciente.paridade, key, value)
        else:
            db_paridade = models.Paridade(
                **paciente.paridade.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_paridade)
    
    # História da Doença
    if paciente.historia_doenca:
        if db_paciente.historia_doenca:
            for key, value in paciente.historia_doenca.dict().items():
                setattr(db_paciente.historia_doenca, key, value)
        else:
            db_hist = models.HistoriaDoenca(
                **paciente.historia_doenca.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_hist)
    
    # Modelos Preditores
    if paciente.modelos_preditores:
        if db_paciente.modelos_preditores:
            for key, value in paciente.modelos_preditores.dict().items():
                setattr(db_paciente.modelos_preditores, key, value)
        else:
            db_modelos = models.ModelosPreditores(
                **paciente.modelos_preditores.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_modelos)
    
    # Tratamento
    if paciente.tratamento:
        if db_paciente.tratamento:
            for key, value in paciente.tratamento.dict().items():
                setattr(db_paciente.tratamento, key, value)
        else:
            db_trat = models.Tratamento(
                **paciente.tratamento.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_trat)
    
    # Desfecho
    if paciente.desfecho:
        if db_paciente.desfecho:
            for key, value in paciente.desfecho.dict().items():
                setattr(db_paciente.desfecho, key, value)
        else:
            db_desf = models.Desfecho(
                **paciente.desfecho.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_desf)
    
    # Tempos Diagnóstico
    if paciente.tempos_diagnostico:
        if db_paciente.tempos_diagnostico:
            for key, value in paciente.tempos_diagnostico.dict().items():
                setattr(db_paciente.tempos_diagnostico, key, value)
        else:
            db_tempos = models.TemposDiagnostico(
                **paciente.tempos_diagnostico.dict(),
                paciente_id=db_paciente.paciente_id
            )
            db.add(db_tempos)


def delete_paciente(db: Session, paciente_id: int):
    """Deleta paciente"""
    paciente = get_paciente(db, paciente_id)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente


def save_historico(db: Session, paciente):
    """Salva histórico de alterações"""
    historico = models.PacienteHistorico(
        paciente_id=paciente.paciente_id,
        data_modificacao=datetime.datetime.utcnow(),
        dados_anteriores={
            "nome_completo": paciente.nome_completo,
            "cpf": paciente.cpf,
            "data_nascimento": str(paciente.data_nascimento) if paciente.data_nascimento else None,
            # Adicionar outros campos conforme necessário
        }
    )
    db.add(historico)
    db.flush()

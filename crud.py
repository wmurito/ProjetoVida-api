from sqlalchemy.orm import Session
import models
import schemas
import datetime

def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    """Cria paciente com todos os dados relacionados"""
    
    # Criar paciente principal
    db_paciente = models.Paciente(**paciente.dict(exclude={
        "familiares", "tratamento", "desfecho"
    }))
    db.add(db_paciente)
    db.flush()
    
    # Familiares
    if paciente.familiares:
        for familiar_data in paciente.familiares:
            db_familiar = models.PacienteFamiliar(
                **familiar_data.dict(),
                id_paciente=db_paciente.id_paciente
            )
            db.add(db_familiar)
    
    # Tratamento
    if paciente.tratamento:
        db_tratamento = models.Tratamento(
            **paciente.tratamento.dict(exclude={
                "cirurgias",
                "quimio_paliativa", "radio_paliativa", "endo_paliativa",
                "imuno_paliativa", "imunohistoquimicas"
            }),
            id_paciente=db_paciente.id_paciente
        )
        db.add(db_tratamento)
        db.flush()
        
        # Cirurgias (Unificadas)
        if paciente.tratamento.cirurgias:
            for cirurgia_data in paciente.tratamento.cirurgias:
                db_cirurgia = models.TratamentoCirurgia(
                    **cirurgia_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_cirurgia)
        
        # Quimioterapia Paliativa
        if paciente.tratamento.quimio_paliativa:
            for quimio_data in paciente.tratamento.quimio_paliativa:
                db_quimio = models.PalliativoQuimioterapia(
                    **quimio_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_quimio)
        
        # Radioterapia Paliativa
        if paciente.tratamento.radio_paliativa:
            for radio_data in paciente.tratamento.radio_paliativa:
                db_radio = models.PalliativoRadioterapia(
                    **radio_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_radio)
        
        # Endocrinoterapia Paliativa
        if paciente.tratamento.endo_paliativa:
            for endo_data in paciente.tratamento.endo_paliativa:
                db_endo = models.PalliativoEndocrinoterapia(
                    **endo_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_endo)
        
        # Imunoterapia Paliativa
        if paciente.tratamento.imuno_paliativa:
            for imuno_data in paciente.tratamento.imuno_paliativa:
                db_imuno = models.PalliativoImunoterapia(
                    **imuno_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_imuno)
        
        # Imunohistoquímicas
        if paciente.tratamento.imunohistoquimicas:
            for imunohisto_data in paciente.tratamento.imunohistoquimicas:
                db_imunohisto = models.Imunohistoquimicas(
                    **imunohisto_data.dict(),
                    id_tratamento=db_tratamento.id_tratamento
                )
                db.add(db_imunohisto)
    
    # Desfecho
    if paciente.desfecho:
        db_desfecho = models.Desfecho(
            **paciente.desfecho.dict(exclude={
                "metastases", "eventos"
            }),
            id_paciente=db_paciente.id_paciente
        )
        db.add(db_desfecho)
        db.flush()
        
        # Metástases
        if paciente.desfecho.metastases:
            for metastase_data in paciente.desfecho.metastases:
                db_metastase = models.DesfechoMetastases(
                    **metastase_data.dict(),
                    id_desfecho=db_desfecho.id_desfecho
                )
                db.add(db_metastase)
        
        # Eventos
        if paciente.desfecho.eventos:
            for evento_data in paciente.desfecho.eventos:
                db_evento = models.DesfechoEventos(
                    **evento_data.dict(),
                    id_desfecho=db_desfecho.id_desfecho
                )
                db.add(db_evento)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def get_paciente(db: Session, paciente_id: int):
    """Busca paciente por ID com todos os relacionamentos"""
    return db.query(models.Paciente).filter(
        models.Paciente.id_paciente == paciente_id
    ).first()


def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista pacientes da tabela PACIENTE com paginação.
    Consulta a tabela principal conforme a modelagem de dados.
    """
    try:
        # Consulta direta na tabela PACIENTE
        pacientes = db.query(models.Paciente).offset(skip).limit(limit).all()
        
        # Log para debug (remover em produção)
        print(f"CRUD: Consultando tabela PACIENTE - {len(pacientes)} registros encontrados")
        
        return pacientes
    except Exception as e:
        print(f"Erro na consulta de pacientes: {str(e)}")
        raise e


def update_paciente(db: Session, paciente_id: int, paciente: schemas.PacienteCreate):
    """Atualiza paciente e todos os relacionamentos"""
    db_paciente = get_paciente(db, paciente_id)
    if not db_paciente:
        return None
    
    # Salvar histórico
    save_historico(db, db_paciente)
    
    # Atualizar dados principais
    for key, value in paciente.dict(exclude={
        "familiares", "tratamento", "desfecho"
    }).items():
        setattr(db_paciente, key, value)
    
    # Atualizar relacionamentos
    update_relacionamentos(db, db_paciente, paciente)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def update_relacionamentos(db: Session, db_paciente, paciente: schemas.PacienteCreate):
    """Atualiza todos os relacionamentos do paciente"""
    
    # Familiares - remover antigos e adicionar novos
    if paciente.familiares is not None:
        for familiar in db_paciente.familiares:
            db.delete(familiar)
        for familiar_data in paciente.familiares:
            db_familiar = models.PacienteFamiliar(
                **familiar_data.dict(),
                id_paciente=db_paciente.id_paciente
            )
            db.add(db_familiar)
    
    # Tratamento
    if paciente.tratamento:
        if db_paciente.tratamento:
            # Atualizar dados principais do tratamento
            for key, value in paciente.tratamento.dict(exclude={
                "cirurgias",
                "quimio_paliativa", "radio_paliativa", "endo_paliativa",
                "imuno_paliativa", "imunohistoquimicas"
            }).items():
                setattr(db_paciente.tratamento, key, value)
            
            # Remover relacionamentos antigos
            for relacionamento in [
                db_paciente.tratamento.cirurgias,
                db_paciente.tratamento.quimio_paliativa,
                db_paciente.tratamento.radio_paliativa,
                db_paciente.tratamento.endo_paliativa,
                db_paciente.tratamento.imuno_paliativa,
                db_paciente.tratamento.imunohistoquimicas
            ]:
                for item in relacionamento:
                    db.delete(item)
        else:
            # Criar novo tratamento
            db_tratamento = models.Tratamento(
                **paciente.tratamento.dict(exclude={
                    "cirurgias",
                    "quimio_paliativa", "radio_paliativa", "endo_paliativa",
                    "imuno_paliativa", "imunohistoquimicas"
                }),
                id_paciente=db_paciente.id_paciente
            )
            db.add(db_tratamento)
            db.flush()
            db_paciente.tratamento = db_tratamento
        
        # Adicionar novos relacionamentos de tratamento
        add_tratamento_relacionamentos(db, db_paciente.tratamento, paciente.tratamento)
    
    # Desfecho
    if paciente.desfecho:
        if db_paciente.desfecho:
            # Atualizar dados principais do desfecho
            for key, value in paciente.desfecho.dict(exclude={
                "metastases", "eventos"
            }).items():
                setattr(db_paciente.desfecho, key, value)
            
            # Remover relacionamentos antigos
            for metastase in db_paciente.desfecho.metastases:
                db.delete(metastase)
            for evento in db_paciente.desfecho.eventos:
                db.delete(evento)
        else:
            # Criar novo desfecho
            db_desfecho = models.Desfecho(
                **paciente.desfecho.dict(exclude={
                    "metastases", "eventos"
                }),
                id_paciente=db_paciente.id_paciente
            )
            db.add(db_desfecho)
            db.flush()
            db_paciente.desfecho = db_desfecho
        
        # Adicionar novos relacionamentos de desfecho
        add_desfecho_relacionamentos(db, db_paciente.desfecho, paciente.desfecho)


def add_tratamento_relacionamentos(db: Session, db_tratamento, tratamento_data):
    """Adiciona relacionamentos de tratamento"""
    
    # Cirurgias (Unificadas)
    if tratamento_data.cirurgias:
        for cirurgia_data in tratamento_data.cirurgias:
            db_cirurgia = models.TratamentoCirurgia(
                **cirurgia_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_cirurgia)
    
    # Quimioterapia Paliativa
    if tratamento_data.quimio_paliativa:
        for quimio_data in tratamento_data.quimio_paliativa:
            db_quimio = models.PalliativoQuimioterapia(
                **quimio_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_quimio)
    
    # Radioterapia Paliativa
    if tratamento_data.radio_paliativa:
        for radio_data in tratamento_data.radio_paliativa:
            db_radio = models.PalliativoRadioterapia(
                **radio_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_radio)
    
    # Endocrinoterapia Paliativa
    if tratamento_data.endo_paliativa:
        for endo_data in tratamento_data.endo_paliativa:
            db_endo = models.PalliativoEndocrinoterapia(
                **endo_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_endo)
    
    # Imunoterapia Paliativa
    if tratamento_data.imuno_paliativa:
        for imuno_data in tratamento_data.imuno_paliativa:
            db_imuno = models.PalliativoImunoterapia(
                **imuno_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_imuno)
    
    # Imunohistoquímicas
    if tratamento_data.imunohistoquimicas:
        for imunohisto_data in tratamento_data.imunohistoquimicas:
            db_imunohisto = models.Imunohistoquimicas(
                **imunohisto_data.dict(),
                id_tratamento=db_tratamento.id_tratamento
            )
            db.add(db_imunohisto)


def add_desfecho_relacionamentos(db: Session, db_desfecho, desfecho_data):
    """Adiciona relacionamentos de desfecho"""
    
    # Metástases
    if desfecho_data.metastases:
        for metastase_data in desfecho_data.metastases:
            db_metastase = models.DesfechoMetastases(
                **metastase_data.dict(),
                id_desfecho=db_desfecho.id_desfecho
            )
            db.add(db_metastase)
    
    # Eventos
    if desfecho_data.eventos:
        for evento_data in desfecho_data.eventos:
            db_evento = models.DesfechoEventos(
                **evento_data.dict(),
                id_desfecho=db_desfecho.id_desfecho
            )
            db.add(db_evento)


def delete_paciente(db: Session, paciente_id: int):
    """Deleta paciente e todos os relacionamentos (CASCADE)"""
    paciente = get_paciente(db, paciente_id)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente


def save_historico(db: Session, paciente):
    """Salva histórico de alterações"""
    historico = models.PacienteHistorico(
        id_paciente=paciente.id_paciente,
        data_modificacao=datetime.datetime.utcnow(),
        dados_anteriores={
            "nome_completo": paciente.nome_completo,
            "data_nascimento": str(paciente.data_nascimento) if paciente.data_nascimento else None,
            "genero": paciente.genero,
            "cidade": paciente.cidade,
            "uf": paciente.uf
        }
    )
    db.add(historico)
    db.flush()


# =======================================================================
# FUNÇÕES ESPECÍFICAS PARA DASHBOARD
# =======================================================================

def get_pacientes_por_estadiamento(db: Session):
    """Retorna contagem de pacientes por estadiamento"""
    from sqlalchemy import func
    
    result = db.query(
        models.Paciente.hd_estadiamento_clinico,
        func.count(models.Paciente.id_paciente).label('count')
    ).group_by(models.Paciente.hd_estadiamento_clinico).all()
    
    return [{"estadiamento": r.hd_estadiamento_clinico or "Não informado", "count": r.count} for r in result]


def get_pacientes_por_status_vital(db: Session):
    """Retorna contagem de pacientes por status vital"""
    from sqlalchemy import func
    
    result = db.query(
        models.Desfecho.status_vital,
        func.count(models.Desfecho.id_desfecho).label('count')
    ).group_by(models.Desfecho.status_vital).all()
    
    return [{"status": r.status_vital or "Não informado", "count": r.count} for r in result]


def get_pacientes_por_recidiva(db: Session):
    """Retorna contagem de pacientes por recidiva"""
    from sqlalchemy import func
    
    result = db.query(
        func.count(models.Desfecho.id_desfecho).label('total'),
        func.sum(func.cast(models.Desfecho.recidiva_local, Integer)).label('recidiva_local'),
        func.sum(func.cast(models.Desfecho.recidiva_regional, Integer)).label('recidiva_regional'),
        func.sum(func.cast(models.Desfecho.metastase_ocorreu, Integer)).label('metastase')
    ).first()
    
    return {
        "total": result.total or 0,
        "recidiva_local": result.recidiva_local or 0,
        "recidiva_regional": result.recidiva_regional or 0,
        "metastase": result.metastase or 0
    }


def get_media_delta_t(db: Session):
    """Calcula média do tempo entre primeira consulta e diagnóstico"""
    from sqlalchemy import func, extract
    
    result = db.query(
        func.avg(
            extract('days', models.Desfecho.td_data_diagnostico - models.Desfecho.td_data_primeira_consulta)
        ).label('media_dias')
    ).filter(
        models.Desfecho.td_data_diagnostico.isnot(None),
        models.Desfecho.td_data_primeira_consulta.isnot(None)
    ).first()
    
    return {"media_dias": float(result.media_dias) if result.media_dias else 0}
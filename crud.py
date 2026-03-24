from sqlalchemy.orm import Session
import models
import schemas
import datetime

def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    """Cria paciente com todos os dados relacionados"""
    
    # Extrair os dados do paciente
    paciente_dict = paciente.dict(exclude={
        "familiares", "tratamento", "desfecho"
    })
    
    # Calcular a idade automaticamente baseada na data de nascimento e momento do cadastro
    if paciente.data_nascimento and not paciente_dict.get('idade'):
        hoje = datetime.date.today()
        idade_calculada = hoje.year - paciente.data_nascimento.year - ((hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day))
        paciente_dict['idade'] = idade_calculada
        
        # Opcionalmente, pode ser útil preencher a idade no diagnóstico para análise
        if paciente_dict.get('hd_idade_diagnostico') is None:
            paciente_dict['hd_idade_diagnostico'] = idade_calculada

    # Criar paciente principal
    db_paciente = models.Paciente(**paciente_dict)
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
    """Busca paciente por ID com todos os relacionamentos carregados"""
    from sqlalchemy.orm import joinedload
    return (
        db.query(models.Paciente)
        .options(
            joinedload(models.Paciente.familiares),
            joinedload(models.Paciente.tratamento).options(
                joinedload(models.Tratamento.cirurgias),
                joinedload(models.Tratamento.quimio_paliativa),
                joinedload(models.Tratamento.radio_paliativa),
                joinedload(models.Tratamento.endo_paliativa),
                joinedload(models.Tratamento.imuno_paliativa),
                joinedload(models.Tratamento.imunohistoquimicas),
            ),
            joinedload(models.Paciente.desfecho).options(
                joinedload(models.Desfecho.metastases),
                joinedload(models.Desfecho.eventos),
            ),
        )
        .filter(models.Paciente.id_paciente == paciente_id)
        .first()
    )


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
    
    # Salvar histórico (não crítico — ignorar se tabela não existir)
    try:
        save_historico(db, db_paciente)
    except Exception as e:
        print(f"AVISO: Não foi possível salvar histórico: {type(e).__name__}: {str(e)}")
        db.rollback()
        # Re-buscar o paciente após rollback
        db_paciente = get_paciente(db, paciente_id)
        if not db_paciente:
            return None

    
    # Extrair novos dados
    paciente_dict = paciente.dict(exclude={
        "familiares", "tratamento", "desfecho"
    })
    
    # Recalcular idade se a data de nascimento for atualizada e a idade vier nula
    if paciente.data_nascimento and not paciente_dict.get('idade'):
        hoje = datetime.date.today()
        idade_calculada = hoje.year - paciente.data_nascimento.year - ((hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day))
        paciente_dict['idade'] = idade_calculada
        
        if paciente_dict.get('hd_idade_diagnostico') is None:
            paciente_dict['hd_idade_diagnostico'] = idade_calculada
    
    # Atualizar dados principais
    for key, value in paciente_dict.items():
        setattr(db_paciente, key, value)
    
    # Atualizar relacionamentos
    update_relacionamentos(db, db_paciente, paciente)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def update_relacionamentos(db: Session, db_paciente, paciente: schemas.PacienteCreate):
    """Atualiza todos os relacionamentos do paciente via queries explícitas (não usa lazy=noload)."""
    paciente_id = db_paciente.id_paciente

    # Familiares - deletar antigos e inserir novos via query direta
    if paciente.familiares is not None:
        db.query(models.PacienteFamiliar).filter(
            models.PacienteFamiliar.id_paciente == paciente_id
        ).delete(synchronize_session=False)
        for familiar_data in paciente.familiares:
            db.add(models.PacienteFamiliar(
                **familiar_data.dict(),
                id_paciente=paciente_id
            ))

    # Tratamento - buscar diretamente pelo id_paciente
    if paciente.tratamento:
        db_tratamento = db.query(models.Tratamento).filter(
            models.Tratamento.id_paciente == paciente_id
        ).first()

        tratamento_campos = paciente.tratamento.dict(exclude={
            "cirurgias", "quimio_paliativa", "radio_paliativa",
            "endo_paliativa", "imuno_paliativa", "imunohistoquimicas"
        })

        if db_tratamento:
            for key, value in tratamento_campos.items():
                setattr(db_tratamento, key, value)
            # Deletar sub-registros antigos
            db.query(models.TratamentoCirurgia).filter(
                models.TratamentoCirurgia.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
            db.query(models.PalliativoQuimioterapia).filter(
                models.PalliativoQuimioterapia.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
            db.query(models.PalliativoRadioterapia).filter(
                models.PalliativoRadioterapia.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
            db.query(models.PalliativoEndocrinoterapia).filter(
                models.PalliativoEndocrinoterapia.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
            db.query(models.PalliativoImunoterapia).filter(
                models.PalliativoImunoterapia.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
            db.query(models.Imunohistoquimicas).filter(
                models.Imunohistoquimicas.id_tratamento == db_tratamento.id_tratamento
            ).delete(synchronize_session=False)
        else:
            db_tratamento = models.Tratamento(**tratamento_campos, id_paciente=paciente_id)
            db.add(db_tratamento)
            db.flush()

        add_tratamento_relacionamentos(db, db_tratamento, paciente.tratamento)

    # Desfecho - buscar diretamente pelo id_paciente
    if paciente.desfecho:
        db_desfecho = db.query(models.Desfecho).filter(
            models.Desfecho.id_paciente == paciente_id
        ).first()

        desfecho_campos = paciente.desfecho.dict(exclude={"metastases", "eventos"})

        if db_desfecho:
            for key, value in desfecho_campos.items():
                setattr(db_desfecho, key, value)
            db.query(models.DesfechoMetastases).filter(
                models.DesfechoMetastases.id_desfecho == db_desfecho.id_desfecho
            ).delete(synchronize_session=False)
            db.query(models.DesfechoEventos).filter(
                models.DesfechoEventos.id_desfecho == db_desfecho.id_desfecho
            ).delete(synchronize_session=False)
        else:
            db_desfecho = models.Desfecho(**desfecho_campos, id_paciente=paciente_id)
            db.add(db_desfecho)
            db.flush()

        add_desfecho_relacionamentos(db, db_desfecho, paciente.desfecho)



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
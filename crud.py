from sqlalchemy.orm import Session
import models
import schemas
import datetime

def create_paciente(db: Session, paciente: schemas.PacienteCreate):
    """Cria paciente com todos os dados relacionados"""
    
    # Criar paciente principal
    db_paciente = models.Paciente(**paciente.dict(exclude={
        "historia_patologica", "historia_familiar", "familiares", "habitos_vida", "paridade",
        "historia_doenca", "modelos_preditores", "tratamento", "desfecho", "tempos_diagnostico"
    }))
    db.add(db_paciente)
    db.flush()
    
    # História Patológica - converter estrutura aninhada
    if paciente.historia_patologica:
        hp = paciente.historia_patologica
        comorbidades = hp.comorbidades or {}
        neoplasia = hp.neoplasia_previa or {}
        biopsia = hp.biopsia_mamaria_previa or {}
        
        db_hist_pat = models.HistoriaPatologica(
            paciente_id=db_paciente.paciente_id,
            comorbidades_has=comorbidades.get('has', False),
            comorbidades_diabetes=comorbidades.get('diabetes', False),
            comorbidades_hipertensao=comorbidades.get('hipertensao', False),
            comorbidades_doenca_cardiaca=comorbidades.get('doenca_cardiaca', False),
            comorbidades_doenca_renal=comorbidades.get('doenca_renal', False),
            comorbidades_doenca_pulmonar=comorbidades.get('doenca_pulmonar', False),
            comorbidades_doenca_figado=comorbidades.get('doenca_figado', False),
            comorbidades_avc=comorbidades.get('avc', False),
            comorbidades_outra=comorbidades.get('outra', ''),
            neoplasia_previa_has=neoplasia.get('has', False),
            neoplasia_previa_qual=neoplasia.get('qual', ''),
            neoplasia_previa_idade_diagnostico=int(neoplasia.get('idade_diagnostico', 0)) if neoplasia.get('idade_diagnostico') else None,
            biopsia_mamaria_previa_has=biopsia.get('has', False),
            biopsia_mamaria_previa_resultado=biopsia.get('resultado', '')
        )
        db.add(db_hist_pat)
    
    # História Familiar
    if paciente.historia_familiar:
        db_hist_fam = models.HistoriaFamiliar(
            paciente_id=db_paciente.paciente_id,
            cancer_familia=paciente.historia_familiar.cancer_familia,
            observacoes=paciente.historia_familiar.observacoes
        )
        db.add(db_hist_fam)
    
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
    try:
        # Tentar buscar com todas as colunas primeiro
        return db.query(models.Paciente).filter(
            models.Paciente.paciente_id == paciente_id
        ).first()
    except Exception as e:
        # Se falhar (provavelmente por coluna CPF não existir), buscar sem CPF
        from sqlalchemy import text
        query = text("""
            SELECT paciente_id, nome_completo, data_nascimento, prontuario, genero, 
                   estado_civil, cor_etnia, escolaridade, renda_familiar, naturalidade, 
                   profissao, cep, logradouro, numero, complemento, bairro, cidade, uf, 
                   telefone, email, altura, peso, imc, idade
            FROM masto.paciente 
            WHERE paciente_id = :paciente_id
        """)
        result = db.execute(query, {"paciente_id": paciente_id}).fetchone()
        
        if result:
            paciente_data = {
                "paciente_id": result[0],
                "nome_completo": result[1],
                "data_nascimento": result[2],
                "prontuario": result[3],
                "genero": result[4],
                "estado_civil": result[5],
                "cor_etnia": result[6],
                "escolaridade": result[7],
                "renda_familiar": result[8],
                "naturalidade": result[9],
                "profissao": result[10],
                "cep": result[11],
                "logradouro": result[12],
                "numero": result[13],
                "complemento": result[14],
                "bairro": result[15],
                "cidade": result[16],
                "uf": result[17],
                "telefone": result[18],
                "email": result[19],
                "altura": result[20],
                "peso": result[21],
                "imc": result[22],
                "idade": result[23]
            }
            return models.Paciente(**paciente_data)
        
        return None


def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    """Lista pacientes"""
    try:
        # Tentar buscar com todas as colunas primeiro
        return db.query(models.Paciente).offset(skip).limit(limit).all()
    except Exception as e:
        # Se falhar (provavelmente por coluna CPF não existir), buscar sem CPF
        from sqlalchemy import text
        query = text("""
            SELECT paciente_id, nome_completo, data_nascimento, prontuario, genero, 
                   estado_civil, cor_etnia, escolaridade, renda_familiar, naturalidade, 
                   profissao, cep, logradouro, numero, complemento, bairro, cidade, uf, 
                   telefone, email, altura, peso, imc, idade
            FROM masto.paciente 
            ORDER BY paciente_id 
            LIMIT :limit OFFSET :skip
        """)
        result = db.execute(query, {"limit": limit, "skip": skip})
        
        # Converter resultado para objetos Paciente
        pacientes = []
        for row in result:
            paciente_data = {
                "paciente_id": row[0],
                "nome_completo": row[1],
                "data_nascimento": row[2],
                "prontuario": row[3],
                "genero": row[4],
                "estado_civil": row[5],
                "cor_etnia": row[6],
                "escolaridade": row[7],
                "renda_familiar": row[8],
                "naturalidade": row[9],
                "profissao": row[10],
                "cep": row[11],
                "logradouro": row[12],
                "numero": row[13],
                "complemento": row[14],
                "bairro": row[15],
                "cidade": row[16],
                "uf": row[17],
                "telefone": row[18],
                "email": row[19],
                "altura": row[20],
                "peso": row[21],
                "imc": row[22],
                "idade": row[23]
            }
            # Criar objeto Paciente com os dados
            paciente = models.Paciente(**paciente_data)
            pacientes.append(paciente)
        
        return pacientes


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
            "data_nascimento": str(paciente.data_nascimento) if paciente.data_nascimento else None,
        }
    )
    db.add(historico)
    db.flush()

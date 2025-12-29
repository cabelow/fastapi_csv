from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import SessionLocal
from models.funcionario import Funcionario
from schemas.funcionario import (
    FuncionarioCreate,
    FuncionarioUpdate,
    FuncionarioResponse
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FuncionarioResponse)
def criar_funcionario(
    payload: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    funcionario = Funcionario(**payload.model_dump())
    db.add(funcionario)
    db.commit()
    db.refresh(funcionario)
    return funcionario

@router.get("/", response_model=list[FuncionarioResponse])
def listar_funcionarios(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    return (
        db.query(Funcionario)
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.get("/{id}", response_model=FuncionarioResponse)
def obter_funcionario(id: int, db: Session = Depends(get_db)):
    funcionario = db.get(Funcionario, id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return funcionario

@router.put("/{id}", response_model=FuncionarioResponse)
def atualizar_funcionario(
    id: int,
    payload: FuncionarioUpdate,
    db: Session = Depends(get_db)
):
    funcionario = db.get(Funcionario, id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    for campo, valor in payload.model_dump().items():
        setattr(funcionario, campo, valor)

    db.commit()
    db.refresh(funcionario)
    return funcionario

@router.delete("/{id}")
def remover_funcionario(id: int, db: Session = Depends(get_db)):
    funcionario = db.get(Funcionario, id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    db.delete(funcionario)
    db.commit()
    return {"mensagem": "Removido com sucesso"}

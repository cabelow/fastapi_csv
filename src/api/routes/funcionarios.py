from datetime import datetime
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

@router.get("/popular")
def popular_funcionarios(db: Session = Depends(get_db)):
    funcionarios = [
        {
            "cpf": "123.456.789-01",
            "nome_funcionario": "João Silva",
            "codigo_cargo": "C001",
            "cargo": "Analista",
            "codigo_unidade": "U001",
            "unidade": "São Paulo",
            "codigo_setor": "S001",
            "setor": "Financeiro",
            "data_admissao": "2020-01-15"
        },
        {
            "cpf": "234.567.890-02",
            "nome_funcionario": "Maria Oliveira",
            "codigo_cargo": "C002",
            "cargo": "Coordenadora",
            "codigo_unidade": "U002",
            "unidade": "Rio de Janeiro",
            "codigo_setor": "S002",
            "setor": "RH",
            "data_admissao": "2019-05-10"
        },
        {
            "cpf": "345.678.901-03",
            "nome_funcionario": "Carlos Pereira",
            "codigo_cargo": "C003",
            "cargo": "Gerente",
            "codigo_unidade": "U001",
            "unidade": "São Paulo",
            "codigo_setor": "S003",
            "setor": "Comercial",
            "data_admissao": "2018-09-20"
        },
        {
            "cpf": "456.789.012-04",
            "nome_funcionario": "Ana Souza",
            "codigo_cargo": "C004",
            "cargo": "Assistente",
            "codigo_unidade": "U003",
            "unidade": "Belo Horizonte",
            "codigo_setor": "S004",
            "setor": "Logística",
            "data_admissao": "2021-03-01"
        },
        {
            "cpf": "567.890.123-05",
            "nome_funcionario": "Rafael Costa",
            "codigo_cargo": "C005",
            "cargo": "Analista",
            "codigo_unidade": "U002",
            "unidade": "Rio de Janeiro",
            "codigo_setor": "S001",
            "setor": "Financeiro",
            "data_admissao": "2022-07-12"
        },
        {
            "cpf": "678.901.234-06",
            "nome_funcionario": "Juliana Lima",
            "codigo_cargo": "C006",
            "cargo": "Assistente",
            "codigo_unidade": "U003",
            "unidade": "Belo Horizonte",
            "codigo_setor": "S002",
            "setor": "RH",
            "data_admissao": "2020-11-23"
        },
        {
            "cpf": "789.012.345-07",
            "nome_funcionario": "Fernando Alves",
            "codigo_cargo": "C007",
            "cargo": "Gerente",
            "codigo_unidade": "U001",
            "unidade": "São Paulo",
            "codigo_setor": "S003",
            "setor": "Comercial",
            "data_admissao": "2017-08-15"
        },
        {
            "cpf": "890.123.456-08",
            "nome_funcionario": "Patrícia Mendes",
            "codigo_cargo": "C008",
            "cargo": "Coordenadora",
            "codigo_unidade": "U002",
            "unidade": "Rio de Janeiro",
            "codigo_setor": "S004",
            "setor": "Logística",
            "data_admissao": "2019-12-05"
        },
        {
            "cpf": "901.234.567-09",
            "nome_funcionario": "Bruno Martins",
            "codigo_cargo": "C009",
            "cargo": "Analista",
            "codigo_unidade": "U003",
            "unidade": "Belo Horizonte",
            "codigo_setor": "S001",
            "setor": "Financeiro",
            "data_admissao": "2021-06-18"
        },
        {
            "cpf": "012.345.678-10",
            "nome_funcionario": "Carla Fernandes",
            "codigo_cargo": "C010",
            "cargo": "Assistente",
            "codigo_unidade": "U001",
            "unidade": "São Paulo",
            "codigo_setor": "S002",
            "setor": "RH",
            "data_admissao": "2020-10-30"
        },
    ]
    for f in funcionarios:
        if isinstance(f["data_admissao"], str):
            f["data_admissao"] = datetime.strptime(f["data_admissao"], "%Y-%m-%d").date()
            funcionario = Funcionario(**f)
            db.add(funcionario)

        db.commit()
    return {"mensagem": "10 funcionários populados com sucesso!"}



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

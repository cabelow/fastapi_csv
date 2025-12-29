from pydantic import BaseModel
from datetime import date

class FuncionarioBase(BaseModel):
    cpf: str
    nome_funcionario: str

    codigo_cargo: str | None = None
    cargo: str | None = None

    codigo_unidade: str | None = None
    unidade: str | None = None

    codigo_setor: str | None = None
    setor: str | None = None

    data_admissao: date | None = None


class FuncionarioCreate(FuncionarioBase):
    pass


class FuncionarioUpdate(FuncionarioBase):
    pass


class FuncionarioResponse(FuncionarioBase):
    id: int

    class Config:
        from_attributes = True

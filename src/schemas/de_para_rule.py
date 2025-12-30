from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeParaRuleBase(BaseModel):
    nome_campo: str
    valor_destino: str
    valores_origem: str


class DeParaRuleCreate(DeParaRuleBase):
    pass


class DeParaRuleUpdate(BaseModel):
    nome_campo: Optional[str]
    valor_destino: Optional[str]
    valores_origem: Optional[str]


class DeParaRuleResponse(DeParaRuleBase):
    id: int

    class Config:
        from_attributes = True

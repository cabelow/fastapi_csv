from sqlalchemy import Column, Integer, String
from database.session import Base

class DeParaRule(Base):
    __tablename__ = "de_para_rules"

    id = Column(Integer, primary_key=True, index=True)
    nome_campo = Column(String(100), index=True, nullable=False)
    valor_destino = Column(String(100), nullable=False)
    valores_origem = Column(String, nullable=False)
    
from sqlalchemy import Column, Integer, String, Date
from database.session import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)

    cpf = Column(String(14), unique=True, nullable=False, index=True)
    nome_funcionario = Column(String(255), nullable=False)

    codigo_cargo = Column(String(20), nullable=True)
    cargo = Column(String(100), nullable=True)

    codigo_unidade = Column(String(20), nullable=True)
    unidade = Column(String(150), nullable=True)

    codigo_setor = Column(String(20), nullable=True)
    setor = Column(String(150), nullable=True)

    data_admissao = Column(Date, nullable=True)

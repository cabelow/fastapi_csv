from sqlalchemy.orm import Session
from models.de_para_rule import DeParaRule


def carregar_de_para_em_memoria(db: Session) -> dict:
    """
    Retorna:
    {
        "department_code": {"d010": "st10"},
        "department_name": {"financeiro": ["fin", "contabilidade"]},
        ...
    }
    """
    regras = db.query(DeParaRule).all()

    resultado: dict[str, dict] = {}

    for regra in regras:
        campo = regra.nome_campo.lower().strip()
        destino = regra.valor_destino.lower().strip()

        valores_origem = [
            v.strip().lower()
            for v in regra.valores_origem.split(",")
            if v.strip()
        ]

        if campo not in resultado:
            resultado[campo] = {}

        if len(valores_origem) == 1:
            resultado[campo][valores_origem[0]] = destino
        else:
            resultado[campo][destino] = valores_origem

    return resultado

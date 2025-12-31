from services.semantic_matcher import similaridade_semantica

from sqlalchemy.orm import Session
from models.de_para_rule import DeParaRule 

DE_PARA_UNIT_CODE = {}
DE_PARA_DEPARTMENT_CODE = {}
DE_PARA_POSITION_CODE = {}
DE_PARA_UNIT_NAME = {}
DE_PARA_DEPARTMENT_NAME = {}
DE_PARA_POSITION_NAME = {}
DE_PARA_EMPLOYMENT_STATUS = {}

def carregar_dados_do_banco(db: Session):
    global DE_PARA_UNIT_CODE, DE_PARA_DEPARTMENT_CODE, DE_PARA_POSITION_CODE
    global DE_PARA_UNIT_NAME, DE_PARA_DEPARTMENT_NAME, DE_PARA_POSITION_NAME, DE_PARA_EMPLOYMENT_STATUS

    regras = db.query(DeParaRule).all()

    for d in [DE_PARA_UNIT_CODE, DE_PARA_DEPARTMENT_CODE, DE_PARA_POSITION_CODE, 
              DE_PARA_UNIT_NAME, DE_PARA_DEPARTMENT_NAME, DE_PARA_POSITION_NAME, DE_PARA_EMPLOYMENT_STATUS]:
        d.clear()

    for r in regras:
        campo = r.nome_campo.lower().strip()
        destino = r.valor_destino
        
        origens = [o.strip() for o in r.valores_origem.replace(';', ',').split(',')]

        for orig in origens:
            if campo == "unit_code": DE_PARA_UNIT_CODE[orig] = destino
            elif campo == "department_code": DE_PARA_DEPARTMENT_CODE[orig] = destino
            elif campo == "position_code": DE_PARA_POSITION_CODE[orig] = destino
            elif campo == "unit_name": DE_PARA_UNIT_NAME[orig] = destino
            elif campo == "department_name": DE_PARA_DEPARTMENT_NAME[orig] = destino
            elif campo == "position_name": DE_PARA_POSITION_NAME[orig] = destino
            elif campo == "employment_status": DE_PARA_EMPLOYMENT_STATUS[orig] = destino

    print(f"✅ {len(regras)} regras de-para carregadas do SQLite.")

def normalizar_chave(valor: str) -> str:
    return str(valor or "").lower().strip()


def validar_de_para(valor_btp: str, valor_ayz: str, mapa: dict) -> bool:
    v1 = normalizar_chave(valor_btp)
    v2 = normalizar_chave(valor_ayz)

    if not v1 or not v2:
        return False

    if mapa.get(v1) == v2:
        return True

    for canonico, variacoes in mapa.items():
        canonico_norm = normalizar_chave(canonico)

        if isinstance(variacoes, list):
            variacoes_norm = [normalizar_chave(v) for v in variacoes]
            if (v1 == canonico_norm and v2 in variacoes_norm) or \
               (v2 == canonico_norm and v1 in variacoes_norm):
                return True
        else:
            variacao_norm = normalizar_chave(variacoes)
            if (v1 == canonico_norm and v2 == variacao_norm) or \
               (v2 == canonico_norm and v1 == variacao_norm):
                return True

    return False


def match_com_referencia(valor_btp: str, valor_ayz: str, de_para: dict, threshold: float) -> dict:
    v1 = normalizar_chave(valor_btp)
    v2 = normalizar_chave(valor_ayz)

    if v1 == v2:
        return {"status": "match_exato", "score": 1.0}

    if validar_de_para(v1, v2, de_para):
        return {"status": "match_de_para", "score": 1.0}

    candidatos = []
    for canonico, variacoes in de_para.items():
        candidatos.append(normalizar_chave(canonico))
        if isinstance(variacoes, list):
            candidatos.extend(normalizar_chave(v) for v in variacoes)
        else:
            candidatos.append(normalizar_chave(variacoes))

    melhor_score = max(
        [similaridade_semantica(v1, ref) for ref in candidatos] + [0.0]
    )

    if melhor_score >= threshold:
        return {"status": "match_semantico", "score": round(melhor_score, 3)}

    return {"status": "divergente", "score": round(melhor_score, 3)}

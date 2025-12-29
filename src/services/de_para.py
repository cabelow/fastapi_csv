"""
services/de_para.py

Regras de DE–PARA entre BTP e AYZ:
- Validação determinística (sem IA)
- Referência semântica (IA + DE–PARA)
"""

from services.semantic_matcher import similaridade_semantica

# ============================================================
# Utilitários
# ============================================================

def normalizar_chave(valor: str) -> str:
    """Normaliza valores para comparação: lower + trim + proteção contra None"""
    return str(valor or "").lower().strip()


# ============================================================
# DE–PARA determinístico (códigos)
# ============================================================

DE_PARA_DEPARTMENT_CODE = {
    "d010": "st10",
    "d020": "st11",
    "d030": "st12",
    "d040": "st13",
    "d050": "st14",
}

DE_PARA_POSITION_CODE = {
    "p100": "cg100",
    "p101": "cg101",
    "p102": "cg102",
    "p103": "cg103",
    "p104": "cg104",
    "p105": "cg105",
    "p106": "cg106",
    "p107": "cg107",
}

DE_PARA_UNIT_CODE = {
    "u001": "un01",
    "u002": "un02",
    "u003": "un03",
    "u004": "un04",
    "u005": "un05",
    "u006": "un06",
    "u007": "un07",
    "u008": "un08",
    "u009": "un09",
    "u010": "un10",
}

# DE–PARA de nomes/cidades (referência + IA)
DE_PARA_DEPARTMENT_NAME = {
    "tecnologia da informacao": ["ti", "tec info", "tecnologia informação", "tech info", "informática"],
    "recursos humanos": ["rh", "rec humanos", "recursos humanos", "human resources"],
    "financeiro": ["fin", "financeiro", "finance department", "contabilidade"],
    # cidades
    "sao paulo": ["filial", "matriz", "sp", "são paulo", "sao paulo - matriz", "s.p."],
    "rio de janeiro": ["filial", "matriz", "rj", "rio", "rio de janeiro - filial", "r. janeiro"],
    "belo horizonte": ["filial", "matriz", "bh", "belo horizonte - filial", "b. horizonte"],
    "curitiba": ["filial", "matriz", "cwb", "curitiba - filial", "c.itiba"],
}

# ============================================================
# Validação DE–PARA
# ============================================================

def validar_de_para(valor_btp: str, valor_ayz: str, mapa: dict) -> bool:
    """
    Valida se dois valores correspondem via DE–PARA (bidirecional).
    Funciona para códigos ou nomes.
    """
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
            if (v1 == canonico_norm and v2 in variacoes_norm) or (v2 == canonico_norm and v1 in variacoes_norm):
                return True
        else:
            variacao_norm = normalizar_chave(variacoes)
            if (v1 == canonico_norm and v2 == variacao_norm) or (v2 == canonico_norm and v1 == variacao_norm):
                return True

    return False


def match_semantico_com_referencia(valor_btp: str, valor_ayz: str, mapa: dict, threshold: float) -> dict:
    """
    Combina DE–PARA + IA:
    - Se bate exatamente ou DE–PARA -> status match
    - Se IA >= threshold -> status match_semantico
    - Senão -> divergente
    """
    v1 = normalizar_chave(valor_btp)
    v2 = normalizar_chave(valor_ayz)

    if v1 == v2:
        return {"status": "match_exato", "score": 1.0}

    if validar_de_para(v1, v2, mapa):
        return {"status": "match_de_para", "score": 1.0}

    # IA pura contra todos valores do mapa
    candidatos = [normalizar_chave(c) for c in mapa.keys()]
    for vs in mapa.values():
        if isinstance(vs, list):
            candidatos.extend([normalizar_chave(v) for v in vs])
        else:
            candidatos.append(normalizar_chave(vs))

    melhor_score = max([similaridade_semantica(v1, ref) for ref in candidatos] + [0.0])

    if melhor_score >= threshold:
        return {"status": "match_semantico", "score": round(melhor_score, 3)}

    return {"status": "divergente", "score": round(melhor_score, 3)}


def match_com_referencia(valor_btp: str, valor_ayz: str, de_para: dict, threshold: float) -> dict:
    """
    Retorna um dict:
    {
        status: match_exato | match_de_para | match_semantico | divergente,
        score: float
    }
    """
    v1 = valor_btp.lower().strip()
    v2 = valor_ayz.lower().strip()

    if v1 == v2:
        return {"status": "match_exato", "score": 1.0}

    # Checa DE–PARA
    for canonico, variacoes in de_para.items():
        if isinstance(variacoes, list):
            if (v1 == canonico and v2 in variacoes) or (v2 == canonico and v1 in variacoes):
                return {"status": "match_de_para", "score": 1.0}
        else:
            if (v1 == canonico and v2 == variacoes) or (v2 == canonico and v1 == variacoes):
                return {"status": "match_de_para", "score": 1.0}

    # Checa similaridade semântica
    candidatos = list(de_para.keys()) + [v for vs in de_para.values() for v in (vs if isinstance(vs, list) else [vs])]
    melhor_score = max(similaridade_semantica(v1, ref) for ref in candidatos)

    if melhor_score >= threshold:
        return {"status": "match_semantico", "score": round(melhor_score, 3)}

    return {"status": "divergente", "score": round(melhor_score, 3)}

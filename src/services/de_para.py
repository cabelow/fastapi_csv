"""
services/de_para.py

Contém regras de DE–PARA entre BTP e AYZ.
Usado para validação determinística (sem IA) e como referência semântica.
"""


# ============================================================
# Utilidades
# ============================================================

def normalizar_chave(valor: str) -> str:
    """
    Normaliza valores para comparação:
    - lowercase
    - trim
    - protege contra None
    """
    return str(valor or "").lower().strip()


# ============================================================
# DE–PARA DE CÓDIGOS (determinístico, sem IA)
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


# ============================================================
# DE–PARA DE NOMES (referência + IA)
# ============================================================

DE_PARA_DEPARTMENT_NAME = {
    "tecnologia da informacao": ["ti", "tec info", "tecnologia informação", "tech info", "informática"],
    "recursos humanos": ["rh", "rec humanos", "recursos humanos", "human resources"],
    "financeiro": ["fin", "financeiro", "finance department", "contabilidade"],
    "marketing": ["mkt", "marketing", "marketing dept", "comercial marketing"],
    "vendas": ["sales", "vendas", "comercial vendas", "comercial"],
    "juridico": ["juridico", "legal", "legal dept"],
    "administracao": ["adm", "administração", "administration"],
    "suporte": ["support", "suporte", "help desk", "service desk"],
    "logistica": ["logistics", "logistica", "transporte", "supply chain"],
    "pesquisa e desenvolvimento": ["p&d", "pesquisa desenvolvimento", "r&d", "research and development"],
    #cidades
    "sao paulo": ["filial", "matriz", "sp", "são paulo", "sao paulo - matriz", "são paulo - matriz", "s.p."],
    "rio de janeiro": ["filial", "matriz", "rj", "rio", "rio de janeiro - filial", "r. janeiro"],
    "belo horizonte": ["filial", "matriz", "bh", "belo horizonte - filial", "b. horizonte"],
    "curitiba": ["filial", "matriz", "cwb", "curitiba - filial", "c.itiba"],
    "porto alegre": ["filial", "matriz", "poa", "porto alegre - filial", "p. alegre"],
    "salvador": ["filial", "matriz", "ssa", "salvador - filial", "s.ador"],
    "fortaleza": ["filial", "matriz", "for", "fortaleza - filial", "f.aleza"],
    "recife": ["filial", "matriz", "rec", "recife - filial", "r. fice"],
    "brasília": ["filial", "matriz", "bsb", "brasilia", "brasília - filial", "b.ília"],
    "campinas": ["filial", "matriz", "cps", "campinas - filial", "c. mpinas"],
}


# ============================================================
# Validação DE–PARA (bidirecional)
# ============================================================

def validar_de_para(valor_btp: str, valor_ayz: str, mapa: dict) -> bool:
    """
    Valida se dois valores correspondem via DE–PARA.

    Regras:
    - Case-insensitive
    - Bidirecional
    - Funciona para códigos ou nomes
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

            if (v1 == canonico_norm and v2 in variacoes_norm) or \
               (v2 == canonico_norm and v1 in variacoes_norm):
                return True

        else:
            variacao_norm = normalizar_chave(variacoes)

            if (v1 == canonico_norm and v2 == variacao_norm) or \
               (v2 == canonico_norm and v1 == variacao_norm):
                return True

    return False

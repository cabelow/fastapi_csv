# services/integracao.py

from utils.normalizacao import normalizar_cpf, normalizar_texto
from services.semantic_matcher import similaridade_semantica
from services.de_para import (
    DE_PARA_DEPARTMENT_CODE,
    DE_PARA_POSITION_CODE,
    DE_PARA_DEPARTMENT_NAME,
    match_com_referencia,
    validar_de_para,
)

# Thresholds
THRESHOLD_SEMANTICO = 0.85
THRESHOLD_FULLNAME_DEFAULT = 0.5

CAMPOS_DE_PARA = {
    "department_code": DE_PARA_DEPARTMENT_CODE,
    "position_code": DE_PARA_POSITION_CODE,
}

CAMPOS_COMPARACAO = [
    ("full_name", "nome_funcionario"),
    ("unit_code", "cod_unid"),
    ("unit_name", "unidade"),
    ("department_code", "cod_setor"),
    ("department_name", "setor"),
    ("position_code", "cod_cargo"),
    ("position_name", "cargo"),
]

# ============================================================
# Comparação de um campo
# ============================================================
def comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT):
    """
    Retorna dict com:
    {
        "status": aceito | divergente | match_semantico | match_de_para | exato,
        "score": float,
        "regra": regra utilizada
    }
    """

    valor_btp_norm = normalizar_texto(valor_btp)
    valor_ayz_norm = normalizar_texto(valor_ayz)

    if valor_btp_norm == valor_ayz_norm:
        return {"status": "exato", "score": 1.0, "regra": "exato"}

    # DE–PARA para códigos (binário)
    if campo_btp in CAMPOS_DE_PARA:
        aceito = validar_de_para(valor_btp_norm, valor_ayz_norm, CAMPOS_DE_PARA[campo_btp])
        score = 1.0 if aceito else 0.0
        status = "aceito" if aceito else "divergente"
        return {"status": status, "score": score, "regra": "de_para"}

    # department_name e unit_name → DE–PARA + IA
    elif campo_btp in ["department_name", "unit_name"]:
        resultado = match_com_referencia(valor_btp_norm, valor_ayz_norm, DE_PARA_DEPARTMENT_NAME, THRESHOLD_SEMANTICO)
        aceito = resultado["status"] != "divergente"
        score = resultado["score"]
        status = "aceito" if aceito else "divergente"
        return {"status": status, "score": score, "regra": resultado["status"]}

    # full_name → IA apenas
    else:
        score = similaridade_semantica(valor_btp_norm, valor_ayz_norm)
        aceito = score >= threshold_fullname
        status = "aceito" if aceito else "divergente"
        return {"status": status, "score": score, "regra": "semantica"}

# ============================================================
# Processa um funcionário
# ============================================================
def processar_funcionario(btp_row, df_ayz, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT):
    cpf = btp_row["document_number"]
    ayz_match = df_ayz[df_ayz["cpf"] == cpf]

    if ayz_match.empty:
        return {"nao_encontrado": True, "cpf": cpf, "btp_id": btp_row.get("employee_id")}

    ayz_row = ayz_match.iloc[0]
    divergencias = {}
    possui_divergencia_real = False

    for campo_btp, campo_ayz in CAMPOS_COMPARACAO:
        valor_btp = btp_row.get(campo_btp, "")
        valor_ayz = ayz_row.get(campo_ayz, "")
        resultado = comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname)

        divergencias[campo_btp] = {
            "btp": valor_btp,
            "ayz": valor_ayz,
            "status": resultado["status"],
            "score": round(resultado["score"], 3),
            "regra": resultado["regra"],
        }

        if resultado["status"] != "aceito":
            possui_divergencia_real = True

    registro_base = {
        "cpf": cpf,
        "btp_id": btp_row.get("employee_id"),
        "ayz_id": ayz_row.get("cod_func"),
    }

    return {
        "nao_encontrado": False,
        "registro_base": registro_base,
        "divergencias": divergencias,
        "possui_divergencia_real": possui_divergencia_real,
    }

# ============================================================
# Comparar todos os funcionários
# ============================================================
def comparar_funcionarios(df_btp, df_ayz, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT):
    resultado = {
        "matches_exatos": [],
        "matches_semanticos": [],
        "divergencias_reais": [],
        "nao_encontrados": [],
        "resumo": {},
    }

    for _, btp_row in df_btp.iterrows():
        info = processar_funcionario(btp_row, df_ayz, threshold_fullname)

        if info.get("nao_encontrado"):
            resultado["nao_encontrados"].append({
                "cpf": info["cpf"],
                "btp_id": info["btp_id"],
            })
            continue

        registro_base = info["registro_base"]
        divergencias = info["divergencias"]
        possui_divergencia_real = info["possui_divergencia_real"]

        if all(v["status"] == "exato" for v in divergencias.values()):
            resultado["matches_exatos"].append(registro_base)
        elif possui_divergencia_real:
            resultado["divergencias_reais"].append({**registro_base, "divergencias": divergencias})
        else:
            resultado["matches_semanticos"].append({**registro_base, "divergencias": divergencias})

    resultado["resumo"] = {
        "total_btp": len(df_btp),
        "total_ayz": len(df_ayz),
        "matches_exatos": len(resultado["matches_exatos"]),
        "matches_semanticos": len(resultado["matches_semanticos"]),
        "divergencias_reais": len(resultado["divergencias_reais"]),
        "nao_encontrados": len(resultado["nao_encontrados"]),
        "threshold_semantico": THRESHOLD_SEMANTICO,
        "threshold_fullname": threshold_fullname,
    }

    return resultado

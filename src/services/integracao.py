from utils.normalizacao import normalizar_cpf, normalizar_texto
from services.semantic_matcher import similaridade_semantica
from services.de_para import (
    DE_PARA_DEPARTMENT_CODE,
    DE_PARA_POSITION_CODE,
    DE_PARA_DEPARTMENT_NAME,
    validar_de_para,
)


CAMPOS_DE_PARA = {
    "department_code": DE_PARA_DEPARTMENT_CODE,
    "position_code": DE_PARA_POSITION_CODE,
}


SEMANTIC_THRESHOLD = 0.85

CAMPOS_COMPARACAO = [
    ("full_name", "nome_funcionario"),
    ("unit_code", "cod_unid"),
    ("unit_name", "unidade"),
    ("department_code", "cod_setor"),
    ("department_name", "setor"),
    ("position_code", "cod_cargo"),
    ("position_name", "cargo"),
]


def normalizar_dataframes(df_btp, df_ayz):
    df_btp["document_number"] = df_btp["document_number"].apply(normalizar_cpf)
    df_btp["full_name"] = df_btp["full_name"].apply(normalizar_texto)

    df_ayz["cpf"] = df_ayz["cpf"].apply(normalizar_cpf)
    df_ayz["nome_funcionario"] = df_ayz["nome_funcionario"].apply(normalizar_texto)

    return df_btp, df_ayz

def match_com_referencia(
    valor_btp: str,
    valor_ayz: str,
    de_para: dict,
    threshold: float,
) -> dict:
    """
    Retorna:
    {
        status: match_exato | match_de_para | match_semantico | divergente,
        score: float
    }
    """

    v1 = valor_btp.lower().strip()
    v2 = valor_ayz.lower().strip()

    if v1 == v2:
        return {"status": "match_exato", "score": 1.0}

    for canonico, variacoes in de_para.items():
        if v1 == canonico and v2 in variacoes:
            return {"status": "match_de_para", "score": 1.0}
        if v2 == canonico and v1 in variacoes:
            return {"status": "match_de_para", "score": 1.0}

    candidatos = [canonico for canonico in de_para.keys()]
    candidatos += [v for vs in de_para.values() for v in vs]

    melhor_score = 0.0
    for ref in candidatos:
        score = similaridade_semantica(v1, ref)
        melhor_score = max(melhor_score, score)

    if melhor_score >= threshold:
        return {"status": "match_semantico", "score": round(melhor_score, 3)}

    return {"status": "divergente", "score": round(melhor_score, 3)}


def comparar_funcionarios(df_btp, df_ayz, threshold: float):
    resultado = {
        "matches_exatos": [],
        "matches_semanticos": [],
        "divergencias_reais": [],
        "nao_encontrados": [],
        "resumo": {},
    }

    for _, btp_row in df_btp.iterrows():
        cpf = btp_row["document_number"]

        ayz_match = df_ayz[df_ayz["cpf"] == cpf]
        if ayz_match.empty:
            resultado["nao_encontrados"].append({
                "cpf": cpf,
                "btp_id": btp_row.get("employee_id"),
            })
            continue

        ayz_row = ayz_match.iloc[0]
        divergencias = {}
        possui_divergencia_real = False

        for campo_btp, campo_ayz in CAMPOS_COMPARACAO:
            valor_btp = normalizar_texto(btp_row.get(campo_btp, ""))
            valor_ayz = normalizar_texto(ayz_row.get(campo_ayz, ""))

            if valor_btp == valor_ayz:
                continue

            if campo_btp in CAMPOS_DE_PARA:
                aceito = validar_de_para(valor_btp, valor_ayz, CAMPOS_DE_PARA[campo_btp])
                score = 1.0 if aceito else 0.0
                regra = "de_para"

            elif campo_btp == "department_name":
                resultado_match = match_com_referencia(
                    valor_btp,
                    valor_ayz,
                    DE_PARA_DEPARTMENT_NAME,
                    threshold,
                )
                aceito = resultado_match["status"] != "divergente"
                score = resultado_match["score"]
                regra = resultado_match["status"]

            else:
                score = similaridade_semantica(valor_btp, valor_ayz)
                aceito = score >= threshold
                regra = "semantica"

            divergencias[campo_btp] = {
                "btp": valor_btp,
                "ayz": valor_ayz,
                "status": "aceito" if aceito else "divergente",
                "score": round(score, 3),
                "regra": regra,
            }

            if not aceito:
                possui_divergencia_real = True

        registro_base = {
            "cpf": cpf,
            "btp_id": btp_row.get("employee_id"),
            "ayz_id": ayz_row.get("cod_func"),
        }

        if not divergencias:
            resultado["matches_exatos"].append(registro_base)

        elif possui_divergencia_real:
            resultado["divergencias_reais"].append({
                **registro_base,
                "divergencias": divergencias,
            })

        else:
            resultado["matches_semanticos"].append({
                **registro_base,
                "divergencias": divergencias,
            })

    resultado["resumo"] = {
        "total_btp": len(df_btp),
        "total_ayz": len(df_ayz),
        "matches_exatos": len(resultado["matches_exatos"]),
        "matches_semanticos": len(resultado["matches_semanticos"]),
        "divergencias_reais": len(resultado["divergencias_reais"]),
        "nao_encontrados": len(resultado["nao_encontrados"]),
        "threshold_utilizado": threshold,
    }

    return resultado

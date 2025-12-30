import pandas as pd
from services.de_para import (
    DE_PARA_UNIT_CODE,
    match_com_referencia,
    validar_de_para,
    DE_PARA_DEPARTMENT_CODE,
    DE_PARA_POSITION_CODE,
    DE_PARA_DEPARTMENT_NAME,
    DE_PARA_UNIT_NAME,
    DE_PARA_POSITION_NAME,
    DE_PARA_EMPLOYMENT_STATUS
)
from services.semantic_matcher import similaridade_semantica
from utils.normalizacao import normalizar_cpf, normalizar_texto

THRESHOLD_SEMANTICO_DEFAULT = 0.85
THRESHOLD_FULLNAME_DEFAULT = 0.5

CAMPOS_DE_PARA = {
    "department_code": DE_PARA_DEPARTMENT_CODE,
    "position_code": DE_PARA_POSITION_CODE,
    "unit_code": DE_PARA_UNIT_CODE,
}

CAMPOS_DE_PARA_NAME = {
    "unit_name": DE_PARA_UNIT_NAME,
    "department_name": DE_PARA_DEPARTMENT_NAME,
    "position_name": DE_PARA_POSITION_NAME,
    "employment_status": DE_PARA_EMPLOYMENT_STATUS
}

CAMPOS_COMPARACAO = [
    ("full_name", "nome_funcionario"),
    ("unit_code", "cod_unid"),
    ("unit_name", "unidade"),
    ("department_code", "cod_setor"),
    ("department_name", "setor"),
    ("position_code", "cod_cargo"),
    ("position_name", "cargo"),
    ("hire_date", "data_admissao"),
    ("monthly_salary", "salario"),
    ("employment_status", "status")
]


def comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname, threshold_semantico):
    valor_btp_norm = normalizar_texto(valor_btp)
    valor_ayz_norm = normalizar_texto(valor_ayz)

    if valor_btp_norm == valor_ayz_norm:
        return {"status": "exato", "score": 1.0, "regra": "exato", "aceito": True}

    if campo_btp in CAMPOS_DE_PARA:
        aceito = validar_de_para(valor_btp_norm, valor_ayz_norm, CAMPOS_DE_PARA[campo_btp])
        status = "aprovado regra DE-PARA" if aceito else "reprovado regra DE-PARA"
        return {"status": status, "score": 1.0 if aceito else 0.0, "regra": "de_para", "aceito": aceito}

    elif campo_btp in CAMPOS_DE_PARA_NAME:
        resultado = match_com_referencia(valor_btp_norm, valor_ayz_norm, CAMPOS_DE_PARA_NAME[campo_btp], threshold_semantico)
        aceito = resultado["status"] != "divergente"
        status = "aprovado DE-PARA com IA" if aceito else "reprovado DE-PARA com IA"
        return {"status": status, "score": resultado["score"], "regra": resultado["status"], "aceito": aceito}
        

    else:
        score = similaridade_semantica(valor_btp_norm, valor_ayz_norm)
        aceito = score >= threshold_fullname
        status = "aprovado por IA" if aceito else "reprovado por IA"
        return {"status": status, "score": score, "regra": "semantica", "aceito": aceito}


def processar_funcionario(btp_row, df_ayz, threshold_fullname, threshold_semantico):
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
        resultado = comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname, threshold_semantico)

        divergencias[campo_btp] = {
            "btp": valor_btp,
            "ayz": valor_ayz,
            "status": resultado["status"],
            "score": round(resultado["score"], 3),
            "regra": resultado["regra"],
        }

        if not resultado["aceito"]:
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


def comparar_funcionarios(df_btp, df_ayz, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT, threshold_semantico=THRESHOLD_SEMANTICO_DEFAULT):
    resultado = {
        "matches_exatos": [],
        "matches_semanticos": [],
        "divergencias_reais": [],
        "nao_encontrados": [],
        "resumo": {},
    }

    for _, btp_row in df_btp.iterrows():
        info = processar_funcionario(btp_row, df_ayz, threshold_fullname, threshold_semantico)

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
        "threshold_semantico": threshold_semantico,
        "threshold_fullname": threshold_fullname,
    }

    return resultado

import pandas as pd
from services import de_para as dp_service 
from services.de_para import match_com_referencia, validar_de_para
from services.semantic_matcher import similaridade_semantica
from utils.normalizacao import normalizar_texto

THRESHOLD_SEMANTICO_DEFAULT = 0.85
THRESHOLD_FULLNAME_DEFAULT = 0.5

CAMPOS_COMPARACAO = [
    ("document_number", "cpf"),
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

def comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname, threshold_semantico, c_de_para_cod, c_de_para_name):
    """Compara os campos usando os dicionários carregados do banco."""
    vazio_btp = pd.isna(valor_btp) or str(valor_btp).strip() == ""
    vazio_ayz = pd.isna(valor_ayz) or str(valor_ayz).strip() == ""
    
    if vazio_btp or vazio_ayz:
        return {"status": "campo vazio", "score": 0.0, "regra": "validacao", "aceito": False}

    valor_btp_norm = normalizar_texto(valor_btp)
    valor_ayz_norm = normalizar_texto(valor_ayz)

    if valor_btp_norm == valor_ayz_norm:
        return {"status": "exato", "score": 1.0, "regra": "exato", "aceito": True}

    if campo_btp in c_de_para_name:
        resultado = match_com_referencia(valor_btp_norm, valor_ayz_norm, c_de_para_name[campo_btp], threshold_semantico)
        aceito = resultado["status"] != "divergente"
        status = "aprovado DE-PARA com IA" if aceito else "reprovado DE-PARA com IA"
        return {"status": status, "score": resultado["score"], "regra": "ia_referencia", "aceito": aceito}

    elif campo_btp in c_de_para_cod:
        aceito = validar_de_para(valor_btp_norm, valor_ayz_norm, c_de_para_cod[campo_btp])
        status = "aprovado regra DE-PARA" if aceito else "reprovado regra DE-PARA"
        return {"status": status, "score": 1.0 if aceito else 0.0, "regra": "de_para", "aceito": aceito}
        
    else:
        score = similaridade_semantica(valor_btp_norm, valor_ayz_norm)
        aceito = score >= (threshold_fullname if campo_btp == "full_name" else threshold_semantico)
        status = "aprovado por IA" if aceito else "reprovado por IA"
        return {"status": status, "score": score, "regra": "semantica", "aceito": aceito}


def processar_funcionario(btp_row, df_ayz, threshold_fullname, threshold_semantico, c_de_para_cod, c_de_para_name):
    cpf = btp_row.get("document_number")
    cpf_valido = len(str(cpf)) == 11
    ayz_match = df_ayz[df_ayz["cpf"] == cpf]

    if ayz_match.empty:
        return {"nao_encontrado": True, "cpf": cpf, "btp_id": btp_row.get("employee_id"), "cpf_invalido": not cpf_valido}

    ayz_row = ayz_match.iloc[0]
    divergencias = {}
    possui_divergencia_real = False

    for campo_btp, campo_ayz in CAMPOS_COMPARACAO:
        valor_btp = btp_row.get(campo_btp)
        valor_ayz = ayz_row.get(campo_ayz)

        resultado = comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname, threshold_semantico, c_de_para_cod, c_de_para_name)

        divergencias[campo_btp] = {
            "btp": valor_btp,
            "ayz": valor_ayz,
            "status": resultado["status"],
            "score": round(resultado["score"], 3),
            "regra": resultado["regra"],
        }
        if not resultado["aceito"]:
            possui_divergencia_real = True

    return {
        "nao_encontrado": False,
        "registro_base": {
            "cpf": cpf,
            "btp_id": btp_row.get("employee_id"),
            "ayz_id": ayz_row.get("cod_func"),
            "duplicado_no_destino": len(ayz_match) > 1,
            "cpf_mal_formado": not cpf_valido
        },
        "divergencias": divergencias,
        "possui_divergencia_real": possui_divergencia_real or (len(ayz_match) > 1) or not cpf_valido,
    }


def comparar_funcionarios(df_btp, df_ayz, db, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT, threshold_semantico=THRESHOLD_SEMANTICO_DEFAULT):
    """
    Compara os funcionários entre BTP e AYZ, usando DE-PARA carregado do banco.
    """

    dp_service.carregar_dados_do_banco(db)

    c_de_para_cod = {
        "department_code": dp_service.DE_PARA_DEPARTMENT_CODE,
        "position_code": dp_service.DE_PARA_POSITION_CODE,
        "unit_code": dp_service.DE_PARA_UNIT_CODE,
    }
    c_de_para_name = {
        "unit_name": dp_service.DE_PARA_UNIT_NAME,
        "department_name": dp_service.DE_PARA_DEPARTMENT_NAME,
        "position_name": dp_service.DE_PARA_POSITION_NAME,
        "employment_status": dp_service.DE_PARA_EMPLOYMENT_STATUS
    }

    resultado = {
        "matches_exatos": [],
        "matches_semanticos": [],
        "divergencias_reais": [],
        "nao_encontrados": [],
        "alertas_criticos": [],
        "resumo": {},
    }

    for _, btp_row in df_btp.iterrows():
        info = processar_funcionario(
            btp_row,
            df_ayz,
            threshold_fullname,
            threshold_semantico,
            c_de_para_cod,
            c_de_para_name
        )

        if info.get("nao_encontrado"):
            resultado["nao_encontrados"].append({"cpf": info["cpf"], "btp_id": info["btp_id"]})
            continue

        reg_base = info["registro_base"]
        divergencias = info["divergencias"]

        if all(v["status"] == "exato" for v in divergencias.values()):
            resultado["matches_exatos"].append(reg_base)
        elif info["possui_divergencia_real"]:
            resultado["divergencias_reais"].append({**reg_base, "divergencias": divergencias})
        else:
            resultado["matches_semanticos"].append({**reg_base, "divergencias": divergencias})

    resultado["resumo"] = {
        "total_btp": len(df_btp),
        "total_ayz": len(df_ayz),
        "matches_exatos": len(resultado["matches_exatos"]),
        "matches_semanticos": len(resultado["matches_semanticos"]),
        "divergencias_reais": len(resultado["divergencias_reais"]),
        "nao_encontrados": len(resultado["nao_encontrados"]),
    }

    return resultado

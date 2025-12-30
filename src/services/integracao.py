import pandas as pd
from services.de_para import match_com_referencia, validar_de_para
from services.semantic_matcher import similaridade_semantica
from utils.normalizacao import normalizar_cpf, normalizar_texto
from services.de_para_loader import carregar_de_para_em_memoria

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
]

CAMPOS_DE_PARA = {}
CAMPOS_DE_PARA_NAME = {}

def inicializar_de_para(db):
    """
    Carrega os DE-PARA do banco e popula os vetores usados pelo integracao.py
    """
    global CAMPOS_DE_PARA, CAMPOS_DE_PARA_NAME
    de_para = carregar_de_para_em_memoria(db)

    CAMPOS_DE_PARA = {
        "department_code": de_para.get("department_code", {}),
        "position_code": de_para.get("position_code", {}),
        "unit_code": de_para.get("unit_code", {}),
    }

    CAMPOS_DE_PARA_NAME = {
        "unit_name": de_para.get("unit_name", {}),
        "department_name": de_para.get("department_name", {}),
        "position_name": de_para.get("position_name", {}),
        "employment_status": de_para.get("employment_status", {}),
    }


def comparar_campo(campo_btp, valor_btp, valor_ayz, threshold_fullname, threshold_semantico):
    vazio_btp = pd.isna(valor_btp) or str(valor_btp).strip() == ""
    vazio_ayz = pd.isna(valor_ayz) or str(valor_ayz).strip() == ""
    
    if vazio_btp or vazio_ayz:
        return {"status": "campo vazio", "score": 0.0, "regra": "validacao", "aceito": False}

    if campo_btp == "monthly_salary" and (float(valor_btp or 0) < 0):
        return {"status": "dados inválidos", "score": 0.0, "regra": "validacao", "aceito": False}
    
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
    
    cpf_valido = len(str(cpf)) == 11
    
    ayz_match = df_ayz[df_ayz["cpf"] == cpf]

    is_duplicate = len(ayz_match) > 1

    if ayz_match.empty:
        return {"nao_encontrado": True, "cpf": cpf, "btp_id": btp_row.get("employee_id"), "cpf_invalido": not cpf_valido}

    ayz_row = ayz_match.iloc[0]
    divergencias = {}
    possui_divergencia_real = False

    for campo_btp, campo_ayz in CAMPOS_COMPARACAO:
        valor_btp = btp_row.get(campo_btp)
        valor_ayz = ayz_row.get(campo_ayz)

        if pd.isna(valor_btp) or str(valor_btp).strip() == "" or pd.isna(valor_ayz) or str(valor_ayz).strip() == "":
            status_erro = "campo_faltando"
            resultado = {"status": status_erro, "score": 0.0, "regra": "validacao", "aceito": False}
        else:
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

    return {
        "nao_encontrado": False,
        "registro_base": {
            "cpf": cpf,
            "btp_id": btp_row.get("employee_id"),
            "ayz_id": ayz_row.get("cod_func"),
            "duplicado_no_destino": is_duplicate,
            "cpf_mal_formado": not cpf_valido
        },
        "divergencias": divergencias,
        "possui_divergencia_real": possui_divergencia_real or is_duplicate or not cpf_valido,
    }


def comparar_funcionarios(df_btp, df_ayz, threshold_fullname=THRESHOLD_FULLNAME_DEFAULT, threshold_semantico=THRESHOLD_SEMANTICO_DEFAULT):
    resultado = {
        "matches_exatos": [],
        "matches_semanticos": [],
        "divergencias_reais": [],
        "nao_encontrados": [],
        "alertas_criticos": [],
        "resumo": {},
    }

    cpfs_duplicados_btp = df_btp[df_btp.duplicated('document_number', keep=False)]['document_number'].unique()
    cpfs_duplicados_ayz = df_ayz[df_ayz.duplicated('cpf', keep=False)]['cpf'].unique()

    for _, btp_row in df_btp.iterrows():
        cpf = btp_row["document_number"]
        info = processar_funcionario(btp_row, df_ayz, threshold_fullname, threshold_semantico)

        if info.get("nao_encontrado"):
            resultado["nao_encontrados"].append({
                "cpf": info["cpf"],
                "btp_id": info["btp_id"],
            })
            
            if cpf in cpfs_duplicados_btp or info.get("cpf_invalido"):
                resultado["alertas_criticos"].append({
                    "cpf": cpf,
                    "btp_id": info["btp_id"],
                    "motivo": "CPF Duplicado no BTP" if cpf in cpfs_duplicados_btp else "CPF Mal Formado",
                    "origem": "BTP"
                })
            continue

        reg_base = info["registro_base"]
        divergencias = info["divergencias"]
        possui_divergencia_real = info["possui_divergencia_real"]

        if cpf in cpfs_duplicados_btp or cpf in cpfs_duplicados_ayz or reg_base.get("cpf_mal_formado"):
            motivos = []
            if cpf in cpfs_duplicados_btp or cpf in cpfs_duplicados_ayz: motivos.append("CPF Duplicado")
            if reg_base.get("cpf_mal_formado"): motivos.append("CPF Mal Formado")
            
            resultado["alertas_criticos"].append({
                "cpf": cpf,
                "btp_id": reg_base["btp_id"],
                "motivo": " e ".join(motivos),
                "origem": "BTP" if cpf in cpfs_duplicados_btp and cpf not in cpfs_duplicados_ayz else 
                          "AYZ" if cpf in cpfs_duplicados_ayz and cpf not in cpfs_duplicados_btp else "Ambos"
            })

        if all(v["status"] == "exato" for v in divergencias.values()):
            resultado["matches_exatos"].append(reg_base)
        elif possui_divergencia_real:
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
        "alertas_criticos": len(resultado["alertas_criticos"]),
        "threshold_semantico": threshold_semantico,
        "threshold_fullname": threshold_fullname,
    }

    return resultado
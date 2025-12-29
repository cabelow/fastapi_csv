from utils.normalizacao import normalizar_cpf, normalizar_texto

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


def comparar_funcionarios(df_btp, df_ayz):
    resultado = {
        "matches": [],
        "divergencias": [],
        "nao_encontrados": [],
        "resumo": {}
    }

    for _, btp_row in df_btp.iterrows():
        cpf = btp_row["document_number"]
        match = df_ayz[df_ayz["cpf"] == cpf]

        if match.empty:
            resultado["nao_encontrados"].append({
                "cpf": cpf,
                "btp_id": btp_row.get("employee_id")
            })
            continue

        ayz_row = match.iloc[0]
        divergencias = {}

        for campo_btp, campo_ayz in CAMPOS_COMPARACAO:
            if str(btp_row[campo_btp]).strip() != str(ayz_row[campo_ayz]).strip():
                divergencias[campo_btp] = {
                    "btp": btp_row[campo_btp],
                    "ayz": ayz_row[campo_ayz]
                }

        if divergencias:
            resultado["divergencias"].append({
                "cpf": cpf,
                "divergencias": divergencias
            })
        else:
            resultado["matches"].append({
                "cpf": cpf,
                "btp_id": btp_row.get("employee_id"),
                "ayz_id": ayz_row.get("cod_func")
            })

    resultado["resumo"] = {
        "total_btp": len(df_btp),
        "total_ayz": len(df_ayz),
        "matches": len(resultado["matches"]),
        "divergencias": len(resultado["divergencias"]),
        "nao_encontrados": len(resultado["nao_encontrados"]),
    }

    return resultado

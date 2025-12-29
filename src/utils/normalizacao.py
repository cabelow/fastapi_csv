import re
import unicodedata


import unicodedata
import re


def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""

    try:
        texto = texto.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    texto = unicodedata.normalize("NFKC", texto)

    texto = texto.replace("�", " ")

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip().lower()



import re
import pandas as pd

def normalizar_cpf(cpf):
    if pd.isna(cpf):
        return None

    cpf = str(cpf)
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11:
        return cpf
    return cpf



def normalizar_dataframes(df_btp, df_ayz):
    df_btp["document_number"] = df_btp["document_number"].apply(normalizar_cpf)
    df_btp["full_name"] = df_btp["full_name"].apply(normalizar_texto)

    df_ayz["cpf"] = df_ayz["cpf"].apply(normalizar_cpf)
    df_ayz["nome_funcionario"] = df_ayz["nome_funcionario"].apply(normalizar_texto)

    return df_btp, df_ayz
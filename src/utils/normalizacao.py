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

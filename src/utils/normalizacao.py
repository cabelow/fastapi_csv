import pandas as pd
import unicodedata

def normalizar_cpf(cpf: str) -> str:
    if pd.isna(cpf):
        return None
    return "".join(filter(str.isdigit, str(cpf)))

def normalizar_texto(texto: str) -> str:
    if pd.isna(texto):
        return None
    texto = texto.strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return texto

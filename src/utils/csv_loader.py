import pandas as pd

def carregar_btp(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="iso-8859-1")

def carregar_ayz(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="iso-8859-1")

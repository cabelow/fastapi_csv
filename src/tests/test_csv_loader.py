from pathlib import Path
import pandas as pd
from utils.csv_loader import carregar_btp, carregar_ayz

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_carregar_btp():
    path = BASE_DIR / "data" / "btp.csv"
    df = carregar_btp(path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ["employee_id", "full_name", "document_number"]:
        assert col in df.columns

def test_carregar_ayz():
    path = BASE_DIR / "data" / "ayz.csv"
    df = carregar_ayz(path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ["cod_func", "nome_funcionario", "cpf"]:
        assert col in df.columns

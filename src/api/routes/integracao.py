from fastapi import APIRouter
from utils.csv_loader import carregar_btp, carregar_ayz
from services.integracao import (
    normalizar_dataframes,
    comparar_funcionarios,
)

router = APIRouter()

@router.get("/integracao/comparar")
def comparar():
    df_btp = carregar_btp("data/btp.csv")
    df_ayz = carregar_ayz("data/ayz.csv")

    df_btp, df_ayz = normalizar_dataframes(df_btp, df_ayz)
    resultado = comparar_funcionarios(df_btp, df_ayz)

    return {"mapping": resultado}

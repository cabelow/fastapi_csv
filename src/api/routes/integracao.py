from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from core.templates import templates
from utils.csv_loader import carregar_btp, carregar_ayz
from services.integracao import (
    normalizar_dataframes,
    comparar_funcionarios,
)

router = APIRouter()

@router.get("/integracao/comparar")
def comparar(threshold: float = 0.85):
    df_btp = carregar_btp("data/btp.csv")
    df_ayz = carregar_ayz("data/ayz.csv")

    df_btp, df_ayz = normalizar_dataframes(df_btp, df_ayz)
    resultado = comparar_funcionarios(df_btp, df_ayz, threshold)

    return {"mapping": resultado}


@router.get(
    "/integracao/comparar/view",
    response_class=HTMLResponse,
)
def comparar_view(request: Request, threshold: float = 0.85):
    df_btp = carregar_btp("data/btp.csv")
    df_ayz = carregar_ayz("data/ayz.csv")

    df_btp, df_ayz = normalizar_dataframes(df_btp, df_ayz)
    resultado = comparar_funcionarios(df_btp, df_ayz, threshold)

    return templates.TemplateResponse(
        "integracao_comparacao.html",
        {
            "request": request,
            "resultado": resultado,
            "threshold": threshold,
        }
    )


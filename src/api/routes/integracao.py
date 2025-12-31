from fastapi import APIRouter, Depends, Request, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session # Corrigido: deve ser sqlalchemy.orm e não requests
from weasyprint import HTML
import tempfile
import csv
import os
import io
import chardet
import pandas as pd

from core.templates import templates
from utils.csv_loader import carregar_btp, carregar_ayz
from services.integracao import comparar_funcionarios
from utils.normalizacao import normalizar_dataframes
from database.session import get_db

router = APIRouter()

def gerar_resultado(ia_name: float, ia_depara: float, db: Session):
    """Agora recebe o DB para repassar à função de comparação"""
    df_btp = carregar_btp("data/btp.csv")
    df_ayz = carregar_ayz("data/ayz.csv")
    df_btp, df_ayz = normalizar_dataframes(df_btp, df_ayz)
    return comparar_funcionarios(df_btp, df_ayz, db=db, threshold_fullname=ia_name, threshold_semantico=ia_depara)


@router.get("/comparar/view", response_class=HTMLResponse)
def comparar_view(
    request: Request,
    ia_name: float = Query(0.85),
    ia_depara: float = Query(0.85),
    db: Session = Depends(get_db)
):
    resultado = gerar_resultado(ia_name, ia_depara, db)
    return templates.TemplateResponse(
        "integracao_comparacao.html",
        {"request": request, "resultado": resultado, "ia_name": ia_name, "ia_depara": ia_depara}
    )

@router.post("/processar-upload", response_class=HTMLResponse)
async def processar_upload(
    request: Request,
    btp_file: UploadFile,
    ayz_file: UploadFile,
    ia_name: float = Form(0.85),
    ia_depara: float = Form(0.85),
    db: Session = Depends(get_db)
):
    btp_bytes = await btp_file.read()
    encoding_btp = chardet.detect(btp_bytes)['encoding']
    df_btp = pd.read_csv(io.BytesIO(btp_bytes), encoding=encoding_btp)

    ayz_bytes = await ayz_file.read()
    encoding_ayz = chardet.detect(ayz_bytes)['encoding']
    df_ayz = pd.read_csv(io.BytesIO(ayz_bytes), encoding=encoding_ayz)

    df_btp, df_ayz = normalizar_dataframes(df_btp, df_ayz)

    resultado = comparar_funcionarios(df_btp, df_ayz, db=db, threshold_fullname=ia_name, threshold_semantico=ia_depara)

    return templates.TemplateResponse(
        "integracao_comparacao.html",
        {"request": request, "resultado": resultado, "ia_name": ia_name, "ia_depara": ia_depara}
    )

@router.get("/comparar/download/pdf", response_class=FileResponse)
def download_pdf(
    ia_name: float = Query(0.85),
    ia_depara: float = Query(0.85),
    db: Session = Depends(get_db)
):
    resultado = gerar_resultado(ia_name, ia_depara, db)
    
    html_content = templates.get_template("integracao_comparacao.html").render(
        request={"request": None},
        resultado=resultado,
        ia_name=ia_name,
        ia_depara=ia_depara
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        tmp_pdf_path = tmp_pdf.name

    return FileResponse(tmp_pdf_path, media_type="application/pdf", filename="comparacao_btp_ayz.pdf")

@router.get("/comparar/download/csv", response_class=FileResponse)
def download_csv(
    ia_name: float = Query(0.85),
    ia_depara: float = Query(0.85),
    db: Session = Depends(get_db)
):
    resultado = gerar_resultado(ia_name, ia_depara, db)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8") as tmp_csv:
        writer = csv.writer(tmp_csv)
        writer.writerow(["cpf", "btp_id", "ayz_id", "campo", "btp", "ayz", "status", "score", "regra"])

        for item in resultado.get("divergencias_reais", []):
            cpf = item["cpf"]
            btp_id = item["btp_id"]
            ayz_id = item["ayz_id"]
            for campo, val in item["divergencias"].items():
                writer.writerow([
                    cpf, btp_id, ayz_id,
                    campo, val["btp"], val["ayz"], val["status"], val["score"], val["regra"]
                ])
        tmp_csv_path = tmp_csv.name

    return FileResponse(tmp_csv_path, media_type="text/csv", filename="comparacao_btp_ayz.csv")

@router.get("/inicio", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "integracao_inicio.html",
        {"request": request, "resultado": None, "threshold": 0.85, "threshold2": 0.85}
    )
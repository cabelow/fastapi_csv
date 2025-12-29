from fastapi import FastAPI
from api.routes.funcionarios import router as funcionarios_router
from api.routes.integracao import router as integracao_router
from database.session import Base, engine

from models import funcionario

app = FastAPI(title="Bencorp API")

Base.metadata.create_all(bind=engine)

app.include_router(
    funcionarios_router,
    prefix="/funcionarios",
    tags=["Funcionários"]
)

app.include_router(
    integracao_router,
    prefix="/integracao",
    tags=["Integração"]
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from services.de_para_rules_service import DeParaRulesService
from schemas.de_para_rule import (
    DeParaRuleCreate,
    DeParaRuleUpdate,
    DeParaRuleResponse
)

router = APIRouter(prefix="/de-para-rules")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.de_para_rule import DeParaRule

router = APIRouter()

@router.get("/popular")
def popular_de_para_rules(db: Session = Depends(get_db)):
    regras = {
        "department_code": {
            "d010": "st10",
            "d020": "st11",
            "d030": "st12",
            "d040": "st13",
            "d050": "st14",
        },
        "position_code": {
            "p100": "cg100",
            "p101": "cg101",
            "p102": "cg102",
            "p103": "cg103",
            "p104": "cg104",
            "p105": "cg105",
            "p106": "cg106",
            "p107": "cg107",
        },
        "unit_code": {
            "u001": "un01",
            "u002": "un02",
            "u003": "un03",
            "u004": "un04",
            "u005": "un05",
            "u006": "un06",
            "u007": "un07",
            "u008": "un08",
            "u009": "un09",
            "u010": "un10",
        },
        "department_name": {
            "tecnologia da informacao": ["ti", "tec info", "tecnologia informação", "tech info", "informática"],
            "recursos humanos": ["rh", "rec humanos", "recursos humanos", "human resources"],
            "financeiro": ["fin", "financeiro", "finance department", "contabilidade"],
        },
        "position_name": {
            "tecnologia da informacao": ["ti", "tec info", "tecnologia informação", "tech info", "informática"],
            "recursos humanos": ["rh", "rec humanos", "recursos humanos", "human resources"],
            "financeiro": ["fin", "financeiro", "finance department", "contabilidade"],
        },
        "unit_name": {
            "sao paulo": ["filial", "matriz", "sp", "são paulo", "sao paulo - matriz"],
            "rio de janeiro": ["filial", "matriz", "rj", "rio", "rio de janeiro"],
            "belo horizonte": ["filial", "matriz", "bh", "belo horizonte"],
            "curitiba": ["filial", "matriz", "cwb", "curitiba"],
        },
        "employment_status": {
            "ATIVO": ["1", "A", "ACTIVE", "ACTIVE STATUS", "EMPLOYED"],
            "INATIVO": ["0", "I", "INACTIVE", "INACTIVE STATUS", "UNEMPLOYED"],
        },
    }

    total = 0

    for nome_campo, mapa in regras.items():
        for valor_destino, origem in mapa.items():

            valores_origem = (
                ",".join(origem) if isinstance(origem, list) else origem
            )

            existe = (
                db.query(DeParaRule)
                .filter(
                    DeParaRule.nome_campo == nome_campo,
                    DeParaRule.valor_destino == valor_destino
                )
                .first()
            )

            if existe:
                continue

            regra = DeParaRule(
                nome_campo=nome_campo,
                valor_destino=valor_destino,
                valores_origem=valores_origem,
            )

            db.add(regra)
            total += 1

    db.commit()

    return {
        "mensagem": "Regras DE→PARA populadas com sucesso!",
        "regras_criadas": total
    }


@router.get("/", response_model=list[DeParaRuleResponse])
def get_all(db: Session = Depends(get_db)):
    return DeParaRulesService.get_all(db)

@router.get("/{rule_id}", response_model=DeParaRuleResponse)
def get_by_id(rule_id: int, db: Session = Depends(get_db)):
    rule = DeParaRulesService.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    return rule

@router.get("/campo/{nome_campo}", response_model=list[DeParaRuleResponse])
def get_by_campo(nome_campo: str, db: Session = Depends(get_db)):
    return DeParaRulesService.get_by_campo(db, nome_campo)

@router.post("/", response_model=DeParaRuleResponse)
def create(data: DeParaRuleCreate, db: Session = Depends(get_db)):
    return DeParaRulesService.create(db, data)

@router.put("/{rule_id}", response_model=DeParaRuleResponse)
def update(rule_id: int, data: DeParaRuleUpdate, db: Session = Depends(get_db)):
    rule = DeParaRulesService.update(db, rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    return rule

@router.delete("/{rule_id}")
def delete(rule_id: int, db: Session = Depends(get_db)):
    ok = DeParaRulesService.delete(db, rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    return {"message": "Regra removida com sucesso"}

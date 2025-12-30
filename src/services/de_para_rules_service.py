from sqlalchemy.orm import Session
from models.de_para_rule import DeParaRule
from schemas.de_para_rule import (
    DeParaRuleCreate,
    DeParaRuleUpdate
)

class DeParaRulesService:

    @staticmethod
    def get_all(db: Session):
        return db.query(DeParaRule).all()

    @staticmethod
    def get_by_id(db: Session, rule_id: int):
        return (
            db.query(DeParaRule)
            .filter(DeParaRule.id == rule_id)
            .first()
        )

    @staticmethod
    def get_by_campo(db: Session, nome_campo: str):
        return (
            db.query(DeParaRule)
            .filter(DeParaRule.nome_campo == nome_campo)
            .all()
        )

    @staticmethod
    def create(db: Session, data: DeParaRuleCreate):
        rule = DeParaRule(**data.model_dump())
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def update(db: Session, rule_id: int, data: DeParaRuleUpdate):
        rule = (
            db.query(DeParaRule)
            .filter(DeParaRule.id == rule_id)
            .first()
        )

        if not rule:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)

        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def delete(db: Session, rule_id: int):
        rule = (
            db.query(DeParaRule)
            .filter(DeParaRule.id == rule_id)
            .first()
        )

        if not rule:
            return False

        db.delete(rule)
        db.commit()
        return True

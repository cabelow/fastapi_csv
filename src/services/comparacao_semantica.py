import os
from rapidfuzz import fuzz
from utils.normalizacao import normalizar_semantico

USE_AI = os.getenv("USE_SEMANTIC_AI", "false").lower() == "true"

_model = None

def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def fuzzy_match(a: str, b: str, threshold: int = 90) -> bool:
    score = fuzz.token_sort_ratio(a, b)
    return score >= threshold

def semantic_match(a: str, b: str, threshold: float = 0.85) -> bool:
    if not USE_AI:
        return False

    model = _load_model()

    from sentence_transformers import util
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()
    return score >= threshold

def campos_equivalentes(a: str, b: str) -> bool:
    if not a or not b:
        return False

    if normalizar_semantico(a) == normalizar_semantico(b):
        return True

    if fuzzy_match(a, b):
        return True
    
    if semantic_match(a, b):
        return True

    return False

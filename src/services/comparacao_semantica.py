import os
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from utils.normalizacao import normalizar_semantico


import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_SRC = Path(__file__).resolve().parent.parent

_MODEL_PATH = os.path.join(BASE_SRC, "utils", "transformer_model")

_model = SentenceTransformer(_MODEL_PATH)

USE_AI = os.getenv("USE_SEMANTIC_AI", "false").lower() == "true"
_MODEL = None
_MODEL_PATH = "app/transformer_model"

def _load_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(_MODEL_PATH)
    return _MODEL

def fuzzy_match(a: str, b: str, threshold: int = 90) -> bool:
    if not a or not b:
        return False
    return fuzz.token_sort_ratio(a, b) >= threshold

def semantic_match(a: str, b: str, threshold: float = 0.85) -> bool:
    if not USE_AI or not a or not b:
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

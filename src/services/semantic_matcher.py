from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import math
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_SRC = Path(__file__).resolve().parent.parent

_MODEL_PATH = os.path.join(BASE_SRC, "utils", "transformer_model")

_model = SentenceTransformer(_MODEL_PATH)

def similaridade_semantica(texto_a: str, texto_b: str) -> float:
    """
    Retorna score de similaridade semântica entre 0 e 1
    (quanto mais próximo de 1, mais parecido)
    """
    if texto_a is None or texto_b is None:
        return 0.0

    texto_a = str(texto_a).strip()
    texto_b = str(texto_b).strip()

    if not texto_a or not texto_b:
        return 0.0

    embeddings = _model.encode([texto_a, texto_b])

    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    if math.isnan(score):
        return 0.0

    return round(float(score), 4)

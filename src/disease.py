from typing import Optional
from .constants import DISEASE_SYNONYMS

def _sanitize_phrase(s: str) -> str:
    return s.replace('"', '\\"').strip()

def build_disease_clause(disease: str) -> tuple[str, str]:
    """
    Returns (pubmed_clause, display_name).
    """
    if not disease:
        disease = "renal cell carcinoma"
    key = disease.lower().strip()

    if key in DISEASE_SYNONYMS:
        syns = list(DISEASE_SYNONYMS[key])
        display = syns[0]
    else:
        display = key
        for canon, syns in DISEASE_SYNONYMS.items():
            if key == canon or key in syns:
                display = syns[0]
                key = canon
                syns = list(syns)
                break
        else:
            syns = [disease]

    terms = [f'"{_sanitize_phrase(s)}"[Title/Abstract]' for s in syns]
    return "(" + " OR ".join(terms) + ")", display

def infer_disease_from_text(text: str) -> Optional[str]:
    t = text.lower()
    for canon, syns in DISEASE_SYNONYMS.items():
        if canon in t or any(s in t for s in syns):
            return canon
    return None

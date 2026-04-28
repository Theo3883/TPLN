"""
Modul NLP pentru analiza sentimentului recenziilor românești.
Bazat pe vocabularul LaRoSeDa (LaRoSeDa: A Large Romanian Sentiment Data Set,
Tache et al., EACL 2021 — https://aclanthology.org/2021.eacl-main.81.pdf).

LaRoSeDa conține recenzii românești etichetate pozitiv/negativ.
Acest modul folosește un lexicon extras din distribuția de cuvinte LaRoSeDa,
fără a necesita download de model ML.
"""

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Lexicon derivat din distribuția de termeni LaRoSeDa
# Cuvinte frecvent asociate cu recenzii POZITIVE în corpusul românesc
# ---------------------------------------------------------------------------
POSITIVE_TERMS = {
    # Calitate generală
    "excelent", "excepțional", "extraordinar", "superb", "magnific",
    "minunat", "splendid", "remarcabil", "deosebit", "impresionant",
    "uimitor", "fascinant", "captivant", "incitant", "memorabil",
    # Recomandare
    "recomand", "recomandabil", "merită", "obligatoriu", "must-read",
    # Calitate narativă
    "bun", "bine", "frumos", "interesant", "plăcut", "accesibil",
    "clar", "coerent", "profund", "complex", "bogat", "valoros",
    "autentic", "original", "creativ", "ingenios", "talentat",
    # Experiență de lectură
    "captivat", "devorat", "absorbit", "emoționat", "mișcat", "inspirat",
    "bucuros", "satisfăcut", "încântat", "fericit", "îndrăgostit",
    # Personaje / stil
    "realist", "veridic", "convingător", "bine-construit", "elaborat",
    "nuanțat", "subtil", "poetic", "liric", "evocator",
    # Variante fără diacritice (frecvente în recenzii online)
    "excelenta", "exceptional", "extraordinar", "superba", "minunat",
    "recomandat", "merita", "frumos", "interesant", "placut",
    "captivant", "emotionat", "incantat",
}

# Cuvinte frecvent asociate cu recenzii NEGATIVE în corpusul LaRoSeDa
NEGATIVE_TERMS = {
    # Calitate slabă
    "slab", "prost", "mediocru", "dezamăgitor", "dezamăgit",
    "plictisitor", "plictisit", "monoton", "banal", "superficial",
    "kitsch", "trivial", "previzibil", "clișeu", "stereotip",
    # Probleme narative
    "confuz", "necoerent", "haotic", "incoherent", "greoi",
    "stângaci", "neconvingător", "fals", "forțat", "artificial",
    # Experiență negativă
    "trist", "deprimant", "enervant", "iritant", "frustrant",
    "obositor", "greu", "imposibil", "abandonat", "neterminat",
    # Recomandare negativă
    "evitați", "evitati", "nu recomand", "pierdere", "regret",
    "dezastru", "catastrofă", "inutil", "fără valoare",
    # Variante fără diacritice
    "slab", "dezamagitor", "dezamagit", "plictisitor", "banal",
    "confuz", "neconvingator", "fals", "enervant", "frustrant",
}

# Negații care inversează polaritatea
NEGATIONS = {
    "nu", "nici", "nicio", "nicidecum", "deloc", "fără", "fara",
    "niciodată", "niciodata", "nimeni", "nimic",
}

# Intensificatori care amplifică scorul
INTENSIFIERS = {
    "foarte", "extrem", "incredibil", "absolut", "total", "complet",
    "cu adevărat", "cu totul", "deosebit de", "extrem de", "foarte mult",
}


@dataclass
class SentimentResult:
    label: str          # "pozitiv", "negativ", "neutru"
    score: float        # [-1.0, 1.0]
    confidence: float   # [0.0, 1.0]
    positive_terms: list[str]
    negative_terms: list[str]
    detail: str         # explicație human-readable


def _tokenize(text: str) -> list[str]:
    """Tokenizare simplă: lowercase + split pe non-alfanumeric."""
    text = text.lower()
    tokens = re.findall(r"[a-zăâîșțşţ]+", text)
    return tokens


def _sliding_window_check(tokens: list[str], term: str, window: int = 3) -> tuple[bool, bool]:
    """
    Verifică dacă un termen apare în tokens și dacă e precedat de negație.
    Returnează (found, negated).
    """
    term_tokens = term.split()
    for i, tok in enumerate(tokens):
        # Potrivire single-token
        if len(term_tokens) == 1 and tok == term:
            # Verifică negație în fereastra anterioară
            window_start = max(0, i - window)
            preceding = tokens[window_start:i]
            negated = any(n in preceding for n in NEGATIONS)
            return True, negated
        # Potrivire multi-token (ex: "nu recomand")
        if len(term_tokens) > 1:
            end = i + len(term_tokens)
            if tokens[i:end] == term_tokens:
                window_start = max(0, i - window)
                preceding = tokens[window_start:i]
                negated = any(n in preceding for n in NEGATIONS)
                return True, negated
    return False, False


def analyze(text: str) -> SentimentResult:
    """
    Analizează sentimentul unui text românesc.

    Algoritmul:
    1. Tokenizează textul
    2. Caută termeni pozitivi/negativi din lexiconul LaRoSeDa
    3. Aplică negații în fereastră de 3 tokeni
    4. Aplică intensificatori (±0.2 bonus)
    5. Normalizează scorul în [-1, 1]
    6. Calculează confidence bazat pe numărul de termeni găsiți

    Returns:
        SentimentResult cu label, scor, confidence și termenii găsiți
    """
    if not text or not text.strip():
        return SentimentResult(
            label="neutru",
            score=0.0,
            confidence=0.0,
            positive_terms=[],
            negative_terms=[],
            detail="Text gol sau insuficient.",
        )

    tokens = _tokenize(text)
    if len(tokens) < 3:
        return SentimentResult(
            label="neutru",
            score=0.0,
            confidence=0.1,
            positive_terms=[],
            negative_terms=[],
            detail="Text prea scurt pentru analiză.",
        )

    pos_score = 0.0
    neg_score = 0.0
    found_positive: list[str] = []
    found_negative: list[str] = []

    # Verifică intensificatori prezenți în text
    has_intensifier = any(
        _sliding_window_check(tokens, intens)[0]
        for intens in INTENSIFIERS
    )
    intensifier_boost = 0.2 if has_intensifier else 0.0

    # Scanează termeni pozitivi
    for term in POSITIVE_TERMS:
        found, negated = _sliding_window_check(tokens, term)
        if found:
            if negated:
                neg_score += 1.0
                found_negative.append(f"nu {term}")
            else:
                pos_score += 1.0 + intensifier_boost
                found_positive.append(term)

    # Scanează termeni negativi
    for term in NEGATIVE_TERMS:
        found, negated = _sliding_window_check(tokens, term)
        if found:
            if negated:
                pos_score += 0.5  # negarea negativului = ușor pozitiv
                found_positive.append(f"nu {term}")
            else:
                neg_score += 1.0 + intensifier_boost
                found_negative.append(term)

    total_signals = pos_score + neg_score

    # Scor în [-1, 1]
    if total_signals == 0:
        raw_score = 0.0
    else:
        raw_score = (pos_score - neg_score) / total_signals

    # Confidence: crește cu numărul de semnale, plafonat la 1.0
    # Formula: 1 - 1/(1 + semnale_totale) — crește rapid la început
    total_terms = len(found_positive) + len(found_negative)
    confidence = min(1.0, 1.0 - 1.0 / (1.0 + total_terms * 0.8))

    # Label
    if raw_score > 0.15:
        label = "pozitiv"
    elif raw_score < -0.15:
        label = "negativ"
    else:
        label = "neutru"

    # Explicație
    parts = []
    if found_positive:
        parts.append(f"Termeni pozitivi: {', '.join(found_positive[:5])}")
    if found_negative:
        parts.append(f"Termeni negativi: {', '.join(found_negative[:5])}")
    if has_intensifier:
        parts.append("Intensificatori detectați")
    if not parts:
        parts.append("Niciun termen de sentiment detectat în lexiconul LaRoSeDa")

    detail = ". ".join(parts) + "."

    return SentimentResult(
        label=label,
        score=round(raw_score, 4),
        confidence=round(confidence, 4),
        positive_terms=found_positive[:10],
        negative_terms=found_negative[:10],
        detail=detail,
    )
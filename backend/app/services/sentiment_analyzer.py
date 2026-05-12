"""
Service pentru analiza automată a sentiment-ului recenziilor.
Integrează modulul NLP existent (nlp/sentiment/analyzer.py).
"""

import sys
from pathlib import Path

# Add NLP module to path
nlp_path = Path(__file__).parent.parent.parent.parent / "nlp"
if str(nlp_path) not in sys.path:
    sys.path.insert(0, str(nlp_path))

from sentiment.analyzer import analyze as nlp_analyze


async def analyze_review_sentiment(text: str) -> dict:
    """
    Analizează sentiment-ul unui text de review.
    
    Args:
        text: Textul recenziei în limba română
        
    Returns:
        dict cu:
            - label: "pozitiv" | "negativ" | "neutru"
            - score: float în [-1.0, 1.0]
            - confidence: float în [0.0, 1.0]
    """
    if not text or not text.strip():
        return {
            "label": "neutru",
            "score": 0.0,
            "confidence": 0.0
        }
    
    # Call NLP analyzer
    result = nlp_analyze(text)
    
    return {
        "label": result.label,
        "score": result.score,
        "confidence": result.confidence
    }

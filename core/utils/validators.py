# core/utils/validators.py
import re

BAD_WORDS = {
    "puta", "viado", "bicha", "arrombado", "caralho", "porra", "desgraça",
    "idiota", "retardado", "macaco", "nazista", "estupro", "matar", "suicida", "biscate", "lixo" 
}

def normalize_phone_br(raw: str) -> str:
    """
    Aceita: (15) 99123-4567, +55 15 991234567, 15991234567...
    Retorna somente dígitos com DDI opcional removido e valida tamanho BR (10 ou 11).
    """
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)

    # remove +55 se vier
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]

    # BR: 10 (fixo) ou 11 (celular com 9)
    if len(digits) not in (10, 11):
        return ""

    return digits

def contains_bad_words(*fields: str) -> bool:
    text = " ".join([f or "" for f in fields]).lower()
    return any(w in text for w in BAD_WORDS)

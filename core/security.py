# core/security.py
import re
from django.utils.html import strip_tags

BAD_WORDS = {
    # ajuste depois — MVP só precisa do básico
    "matar", "suic", "bomba", "arma", "odio", "naz", "estupr",
    "vaga de emprego", "pix grátis", "golpe",
}

def normalize_whatsapp(raw: str) -> str:
    """
    Normaliza para +55DD9XXXXXXXX
    Aceita entradas com espaços/traços/parênteses e com/sem +55.
    """
    if not raw:
        return ""

    digits = re.sub(r"\D+", "", raw)

    # Se veio com 00 (ex: 0055...), tira prefixo internacional genérico
    if digits.startswith("00"):
        digits = digits[2:]

    # Se não tem DDI, assume BR
    if not digits.startswith("55"):
        digits = "55" + digits

    # Agora precisa ter 55 + DDD(2) + número(9)
    # total = 13 dígitos (55 + 2 + 9)
    if len(digits) != 13:
        return ""

    ddd = digits[2:4]
    number = digits[4:]

    # regra simples: celular BR começa com 9 e DDD não pode ser "00"
    if ddd == "00" or not number.startswith("9"):
        return ""

    return f"+{digits}"

def clean_text(raw: str, max_len: int = 120) -> str:
    if not raw:
        return ""
    txt = strip_tags(raw)              # remove HTML
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:max_len]

def has_bad_words(*texts: str) -> bool:
    blob = " ".join(t.lower() for t in texts if t)
    return any(w in blob for w in BAD_WORDS)

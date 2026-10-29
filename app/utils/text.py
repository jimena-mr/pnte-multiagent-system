"""Utilidades de normalización y procesamiento de texto."""

import unicodedata


def normalize_text(text: str) -> str:
    """Normaliza un texto eliminando tildes y pasando a minúsculas para comparaciones robustas."""
    if not text:
        return ""
    # Descomponer caracteres con acento y descartar marcas diacríticas
    nfkd_form = unicodedata.normalize("NFKD", text)
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
    return only_ascii.lower().strip()

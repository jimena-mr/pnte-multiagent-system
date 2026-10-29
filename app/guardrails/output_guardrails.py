"""Validaciones y controles de salida (Output Guardrails) para el asistente del PNTE."""

from typing import Tuple, List
from app.config import get_settings

settings = get_settings()


def enforce_output_guardrails(
    response_text: str,
    in_scope: bool = True,
    max_chars: int = 250,
) -> Tuple[str, List[str]]:
    """
    Aplica controles estrictos a la respuesta del asistente:
    1. Si está fuera de alcance, devuelve el mensaje estándar del PNTE.
    2. Garantiza un máximo estricto de 250 caracteres.
    3. Asegura tono limpio, sin encabezados markdown pesados.
    
    Retorna: (sanitized_response, flags)
    """
    flags: List[str] = []

    # 1. Verificación de alcance
    if not in_scope:
        flags.append("out_of_scope_replaced")
        return settings.system_scope_rejection, flags

    # 2. Limpieza de texto
    cleaned = response_text.strip()
    # Eliminar encabezados tipo Markdown (# Titulo)
    lines = cleaned.splitlines()
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped:
            filtered_lines.append(stripped)
    cleaned = " ".join(filtered_lines)

    # 3. Verificación de longitud estricta (máximo 250 caracteres)
    if len(cleaned) <= max_chars:
        return cleaned, flags

    # Si excede los 250 caracteres, recortar de forma inteligente
    flags.append("truncated_to_max_chars")
    truncated = cleaned[:max_chars].rstrip()

    # Intentar cortar en el último signo de puntuación (. ! ?) dentro del límite
    last_punct = max(
        truncated.rfind("."),
        truncated.rfind("!"),
        truncated.rfind("?"),
    )

    if last_punct > 120:  # Si encontramos una oración con sentido razonable
        final_text = truncated[: last_punct + 1]
    else:
        # Cortar en el último espacio y agregar punto o elipsis
        last_space = truncated.rfind(" ")
        if last_space > 0:
            final_text = truncated[:last_space] + "..."
        else:
            final_text = truncated[: max_chars - 3] + "..."

    # Garantizar que no supere bajo ninguna circunstancia los 250 caracteres
    if len(final_text) > max_chars:
        final_text = final_text[:max_chars]

    return final_text, flags

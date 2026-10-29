"""Filtros y validaciones de entrada (Input Guardrails) para el asistente del PNTE."""

import re
from typing import Tuple

# Palabras clave y temas estrictamente dentro del ámbito del PNTE
IN_SCOPE_KEYWORDS = [
    "formaliza", "constitu", "empresa", "negocio", "emprend",
    "ruc", "sunarp", "sunat", "notaria", "minuta", "reserva de nombre",
    "eirl", "srl", "sac", "sacs", "sociedad", "persona natural",
    "tributo", "tributario", "regimen", "nrus", "rus", "rer", "rmt",
    "general", "factura", "boleta", "impuesto", "igv", "renta",
    "costo", "tarifa", "cuanto cuesta", "precio", "gratis", "uit",
    "sede", "oficina", "asesor", "contacto", "telefono", "direccion",
    "requisito", "capital", "socio", "objeto social", "pnte", "produce",
    "hola", "buenos dias", "buenas tardes", "buenas noches", "gracias",
    "ayuda", "menu", "opciones", "empezar", "inicio", "si", "no"
]

# Patrones sospechosos de prompt injection o jailbreak
INJECTION_PATTERNS = [
    r"ignora (todas )?(las )?instrucciones",
    r"ignore previous instructions",
    r"eres ahora",
    r"you are now",
    r"act as",
    r"system prompt",
    r"dan mode",
    r"olvida tus reglas",
]


def validate_input(user_message: str) -> Tuple[bool, bool, str]:
    """
    Evalúa la seguridad y alcance del mensaje del usuario.
    Retorna: (is_safe, in_scope, reason)
    """
    cleaned = user_message.strip()
    if not cleaned:
        return False, False, "Mensaje vacío"

    # 1. Chequeo de seguridad y prompt injection
    lower_msg = cleaned.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower_msg):
            return False, False, "Posible inyección de instrucciones detectada"

    # 2. Chequeo de temas fuera de alcance
    # Saludos o respuestas cortas permitidas siempre
    if len(lower_msg.split()) <= 2 and any(w in lower_msg for w in ["hola", "buenos", "buenas", "si", "no", "ok", "gracias", "menu", "1", "2", "3", "4", "5"]):
        return True, True, "Interacción conversacional básica"

    # Verificamos si contiene palabras clave del dominio
    has_domain_keyword = any(kw in lower_msg for kw in IN_SCOPE_KEYWORDS)

    # Detección explícita de temas completamente ajenos
    out_of_scope_topics = [
        "futbol", "receta", "cocinar", "pelicula", "musica", "poema",
        "chiste", "codigo python", "javascript", "clima", "politica",
        "elecciones", "presidente", "marca indecopi", "indecopi"
    ]
    if any(topic in lower_msg for topic in out_of_scope_topics) and not has_domain_keyword:
        return True, False, "Tema fuera del alcance de formalización PNTE"

    # Si no tiene ninguna palabra del dominio y tiene más de 3 palabras
    if not has_domain_keyword and len(lower_msg.split()) > 3:
        return True, False, "Consulta no relacionada con formalización y constitución de empresas"

    return True, True, "Mensaje seguro y en alcance"

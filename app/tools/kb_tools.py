"""Herramientas de búsqueda y validación de conocimiento sobre formalización."""

from typing import Dict, Any
from app.data.pnte_knowledge import (
    COMPANY_TYPES,
    RESTRICTED_ACTIVITIES,
    CONSTITUTION_STEPS,
)
from app.utils.text import normalize_text


import re

def search_formalization_kb(query: str) -> str:
    """Busca información oficial sobre tipos de empresas y trámites en el PNTE."""
    query_lower = normalize_text(query)

    # 1. Búsqueda de requisitos específicos
    if any(w in query_lower for w in ["requisito", "documento", "necesito"]):
        return (
            "Requisitos PNTE: 1 a 5 opciones de nombre, DNI vigente de socios/titular, "
            "objeto social detallado, capital social (mín. S/ 1) y declaración jurada."
        )

    # 2. Búsqueda de pasos y etapas del proceso
    if any(w in query_lower for w in ["paso", "etapa", "proceso", "constituir", "tramite"]):
        return (
            "Proceso: 1.Diagnóstico y reserva de nombre (gratis) "
            "2.Acto constitutivo (gratis) 3.Notaría (tarifa social) "
            "4.SUNARP y 5.SUNAT clave SOL."
        )

    # 3. Búsqueda por tipo de empresa exacto con límite de palabra
    for key, info in COMPANY_TYPES.items():
        pattern = r"\b" + re.escape(key) + r"\b"
        name_lower = normalize_text(info["name"])
        if re.search(pattern, query_lower) or name_lower in query_lower:
            return (
                f"{info['name']}: {info['socios']}. {info['responsabilidad']}. "
                f"Capital mínimo {info.get('capital_minimo', 'S/ 1.00')}. {info['descripcion']}"
            )

    return (
        "En PNTE formalizas como Persona Natural con Negocio o Jurídica (EIRL, SRL, SAC, SACS). "
        "Asesoría y reserva de nombre son 100% gratuitas."
    )


def check_restricted_activity(activity_description: str) -> Dict[str, Any]:
    """Verifica si una actividad económica requiere autorización previa o no puede constituirse en PNTE."""
    desc_lower = normalize_text(activity_description)

    for item in RESTRICTED_ACTIVITIES:
        for kw in item["keywords"]:
            if kw in desc_lower:
                if not item["permitido_pnte"]:
                    return {
                        "is_restricted": True,
                        "allowed_in_pnte": False,
                        "reason": item["motivo"],
                        "summary": f"Actividad restringida: {item['motivo']}",
                    }
                else:
                    return {
                        "is_restricted": True,
                        "allowed_in_pnte": True,
                        "condition": item["condicion"],
                        "summary": f"Permitido con condición: {item['condicion']}",
                    }

    return {
        "is_restricted": False,
        "allowed_in_pnte": True,
        "summary": "Actividad económica permitida para constitución regular en PNTE.",
    }

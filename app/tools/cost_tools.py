"""Herramientas de cálculo de costos de constitución y consulta de sedes PNTE."""

from typing import Dict, Any
from app.data.pnte_knowledge import PNTE_SEDES, OFFICIAL_LINKS


def calculate_constitution_costs(
    capital_pen: float = 1000.0,
    uit_value: float = 5350.0,
) -> Dict[str, Any]:
    """Calcula costos de constitución con tarifas preferenciales del PNTE."""
    is_under_or_equal_1_uit = capital_pen <= uit_value

    notary_cost = 120.0
    registry_cost_note = "Exonerado (capital ≤ 1 UIT)" if is_under_or_equal_1_uit else "Aplica tasa SUNARP (supera 1 UIT)"

    summary = (
        f"Costos PNTE: Asesoría, reserva y minuta son GRATIS. "
        f"Notaría desde S/120. Registros públicos: "
        f"{'exonerados por ser ≤ 1 UIT' if is_under_or_equal_1_uit else 'pago adicional al superar 1 UIT'}."
    )

    return {
        "asesoria_pnte": 0.0,
        "reserva_nombre": 0.0,
        "minuta_constitucion": 0.0,
        "notaria_desde": notary_cost,
        "derechos_registrales": registry_cost_note,
        "capital_evaluado": capital_pen,
        "uit_referencia": uit_value,
        "summary": summary[:250],
    }


def get_pnte_office(region: str = "lima") -> str:
    """Obtiene la dirección y atención del Centro de Desarrollo Empresarial (CDE) del PNTE."""
    reg_clean = region.lower().strip()
    for key, data in PNTE_SEDES.items():
        if key in reg_clean or reg_clean in key:
            return (
                f"Sede PNTE en {key.title()}: {data['direccion']}. "
                f"Atención: {data['horario']}. Contacto: {data['contacto']}."
            )[:250]

    return (
        f"PNTE atiende a nivel nacional en Centros MAC y municipios. "
        f"Ubica tu sede más cercana en: {OFFICIAL_LINKS['sedes']} o llama al 016162291."
    )[:250]

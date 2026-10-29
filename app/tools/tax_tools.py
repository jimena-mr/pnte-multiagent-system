"""Herramientas de recomendación y cálculo tributario para emprendedores peruanos."""

from typing import Dict, Any
from app.data.pnte_knowledge import TAX_REGIMES


def recommend_tax_regime(
    annual_sales: float,
    is_juridica: bool = False,
    emite_facturas: bool = True,
) -> Dict[str, Any]:
    """Evalúa ventas estimadas y tipo de empresa para recomendar el mejor régimen tributario."""
    # Si es persona natural, vende <= S/ 96,000 y solo emite boletas
    if not is_juridica and not emite_facturas and annual_sales <= 96000.0:
        regime = TAX_REGIMES["NRUS"]
        cuota = "S/ 20/mes (ventas ≤ S/5,000)" if annual_sales <= 60000.0 else "S/ 50/mes"
        recommendation = (
            f"Te conviene el NRUS: cuota fija de {cuota}, sin libros contables "
            f"ni declaración anual. Solo emites boletas."
        )
        return {
            "recommended_regime": "NRUS",
            "details": regime,
            "summary": recommendation[:250],
        }

    # Si ventas son hasta S/ 525,000
    if annual_sales <= 525000.0:
        regime = TAX_REGIMES["RER"]
        recommendation = (
            "Te conviene el RER: tasa 1.5% de renta mensual + IGV 18%. "
            "Emites facturas y boletas, llevando solo 2 libros (Compras y Ventas)."
        )
        return {
            "recommended_regime": "RER",
            "details": regime,
            "summary": recommendation[:250],
        }

    # Si ventas son de hasta 1700 UIT (ej: 1700 * 5350 = 9,095,000)
    limit_rmt = 1700 * 5350.0
    if annual_sales <= limit_rmt:
        regime = TAX_REGIMES["RMT"]
        recommendation = (
            "Te conviene el Régimen MYPE Tributario (RMT): pago a cuenta de 1% "
            "hasta 300 UIT. Permite deducir gastos reales y emitir todo comprobante."
        )
        return {
            "recommended_regime": "RMT",
            "details": regime,
            "summary": recommendation[:250],
        }

    # Si excede 1700 UIT
    regime = TAX_REGIMES["RG"]
    recommendation = (
        "Corresponde el Régimen General: sin tope de ventas, tasa 1.5% mensual "
        "y regularización anual de 29.5%. Contabilidad completa."
    )
    return {
        "recommended_regime": "RG",
        "details": regime,
        "summary": recommendation[:250],
    }


def get_tax_regime_info(regime_code: str) -> str:
    """Devuelve un resumen conciso del régimen solicitado."""
    code = regime_code.upper().strip()
    if code in TAX_REGIMES:
        info = TAX_REGIMES[code]
        if code == "NRUS":
            return (
                "NRUS: Para personas naturales con ventas hasta S/96,000 al año. "
                "Cuota fija de S/20 o S/50 mensual. Sin libros contables ni IGV aparte."
            )
        elif code == "RER":
            return (
                "RER: Ventas hasta S/525,000/año. Paga 1.5% renta + 18% IGV. "
                "Emites facturas y boletas. Solo libros de Compras y Ventas."
            )
        elif code == "RMT":
            return (
                "RMT: Ventas hasta 1700 UIT. Pago a cuenta de 1% mensual (hasta 300 UIT). "
                "Deduce gastos para pagar menos renta anual. Muy flexible."
            )
        elif code == "RG":
            return (
                "Régimen General: Sin límite de ingresos. Pago a cuenta 1.5% mensual "
                "y 29.5% anual sobre utilidad. Exige contabilidad completa."
            )

    return (
        "Los regímenes en Perú son: NRUS (bodegas/oficios), RER (hasta S/525k), "
        "RMT (hasta 1700 UIT) y RG (sin tope). Todos pagan IGV salvo NRUS."
    )

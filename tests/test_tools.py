"""Pruebas unitarias para las herramientas especializadas del PNTE."""

from app.tools.kb_tools import search_formalization_kb, check_restricted_activity
from app.tools.tax_tools import recommend_tax_regime, get_tax_regime_info
from app.tools.cost_tools import calculate_constitution_costs, get_pnte_office


def test_search_formalization_kb():
    """Valida la recuperación de información sobre formas societarias."""
    res_sac = search_formalization_kb("¿Qué es una SAC?")
    assert "Sociedad Anónima Cerrada" in res_sac
    assert len(res_sac) <= 250

    res_steps = search_formalization_kb("¿Cuáles son los pasos para constituir?")
    assert "Diagnóstico" in res_steps or "Reserva" in res_steps
    assert len(res_steps) <= 250


def test_check_restricted_activity():
    """Verifica la detección de actividades prohibidas y condicionales."""
    # Seguros requiere SBS y S.A.
    check_seguros = check_restricted_activity("Queremos crear una corredora de seguros")
    assert check_seguros["is_restricted"] is True
    assert check_seguros["allowed_in_pnte"] is False
    assert "SBS" in check_seguros["reason"]

    # Universidad requiere SUNEDU
    check_uni = check_restricted_activity("Servicios de educación universitaria y posgrados")
    assert check_uni["is_restricted"] is True
    assert check_uni["allowed_in_pnte"] is False
    assert "SUNEDU" in check_uni["reason"]

    # Venta de ropa es permitida
    check_textil = check_restricted_activity("Venta y confección de prendas textiles")
    assert check_textil["is_restricted"] is False
    assert check_textil["allowed_in_pnte"] is True


def test_recommend_tax_regime():
    """Verifica recomendaciones tributarias según nivel de ventas."""
    # Pequeño negocio persona natural sin facturas
    rec_nrus = recommend_tax_regime(annual_sales=40000.0, is_juridica=False, emite_facturas=False)
    assert rec_nrus["recommended_regime"] == "NRUS"
    assert "NRUS" in rec_nrus["summary"]

    # Empresa con ventas hasta 500k soles
    rec_rer = recommend_tax_regime(annual_sales=200000.0, is_juridica=True, emite_facturas=True)
    assert rec_rer["recommended_regime"] == "RER"
    assert "RER" in rec_rer["summary"]

    # Empresa con ventas de 1 millón de soles
    rec_rmt = recommend_tax_regime(annual_sales=1000000.0, is_juridica=True, emite_facturas=True)
    assert rec_rmt["recommended_regime"] == "RMT"
    assert "RMT" in rec_rmt["summary"]


def test_calculate_constitution_costs():
    """Verifica cálculos de costos notariales y exención registral."""
    # Capital menor o igual a 1 UIT (S/ 5,350)
    cost_low = calculate_constitution_costs(capital_pen=2000.0, uit_value=5350.0)
    assert cost_low["asesoria_pnte"] == 0.0
    assert cost_low["notaria_desde"] == 120.0
    assert "exonerados" in cost_low["summary"] or "Exonerado" in cost_low["derechos_registrales"]

    # Capital mayor a 1 UIT
    cost_high = calculate_constitution_costs(capital_pen=10000.0, uit_value=5350.0)
    assert "superar 1 UIT" in cost_high["summary"]


def test_get_pnte_office():
    """Verifica consulta de sedes y CDE."""
    office_lima = get_pnte_office("lima")
    assert "Lima" in office_lima
    assert "San Isidro" in office_lima or "Centros MAC" in office_lima
    assert len(office_lima) <= 250

    office_unknown = get_pnte_office("loreto")
    assert "sedes" in office_unknown or "016162291" in office_unknown

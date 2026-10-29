"""Base de datos y conocimiento canónico del Programa Nacional Tu Empresa (PNTE)."""

from typing import Dict, List, Any

# Tipos de empresas en Perú
COMPANY_TYPES: Dict[str, Dict[str, Any]] = {
    "natural": {
        "name": "Persona Natural con Negocio",
        "socios": "1 persona (titular)",
        "responsabilidad": "Ilimitada (responde con patrimonio personal)",
        "capital_minimo": "S/ 1.00",
        "descripcion": "Ideal para pequeños negocios, bodegas y oficios individuales.",
        "regimenes_permitidos": ["NRUS", "RER", "RMT", "RG"],
    },
    "eirl": {
        "name": "Empresa Individual de Responsabilidad Limitada (EIRL)",
        "socios": "1 persona (Titular Gerente)",
        "responsabilidad": "Limitada al patrimonio de la empresa",
        "capital_minimo": "S/ 1.00",
        "descripcion": "Una sola persona jurídica, protege tu patrimonio personal.",
        "regimenes_permitidos": ["RER", "RMT", "RG"],
    },
    "srl": {
        "name": "Sociedad Comercial de Responsabilidad Limitada (SRL)",
        "socios": "2 a 20 socios",
        "responsabilidad": "Limitada a los aportes de capital",
        "capital_minimo": "S/ 1.00",
        "descripcion": "Típica para empresas familiares o pocos socios de confianza.",
        "regimenes_permitidos": ["RER", "RMT", "RG"],
    },
    "sac": {
        "name": "Sociedad Anónima Cerrada (SAC)",
        "socios": "2 a 20 socios",
        "responsabilidad": "Limitada al capital en acciones",
        "capital_minimo": "S/ 1.00",
        "directorio": "Opcional",
        "descripcion": "La forma societaria más usada y dinámica para emprendimientos.",
        "regimenes_permitidos": ["RER", "RMT", "RG"],
    },
    "sacs": {
        "name": "Sociedad por Acciones Cerrada Simplificada (SACS)",
        "socios": "2 a 20 personas naturales",
        "responsabilidad": "Limitada al capital en acciones",
        "tramite": "100% digital vía SID-SUNARP con firma digital",
        "capital_minimo": "S/ 1.00",
        "enlace": "https://www.gob.pe/26692-constituir-tu-empresa-como-sociedad-por-acciones-cerradas-simplificadas-sacs",
        "descripcion": "Trámite ágil y digital sin minuta notarial clásica.",
        "regimenes_permitidos": ["RER", "RMT", "RG"],
    },
    "sa": {
        "name": "Sociedad Anónima (SA)",
        "socios": "Mínimo 2, sin límite máximo",
        "responsabilidad": "Limitada",
        "capital_minimo": "S/ 1.00",
        "directorio": "Obligatorio",
        "descripcion": "Para empresas medianas a grandes con estructura corporativa.",
        "regimenes_permitidos": ["RER", "RMT", "RG"],
    },
}

# Regímenes tributarios
TAX_REGIMES: Dict[str, Dict[str, Any]] = {
    "NRUS": {
        "name": "Nuevo Régimen Único Simplificado (NRUS)",
        "aplicable_a": "Solo Personas Naturales con negocio",
        "limite_ventas_anual": 96000.0,
        "limite_ventas_mensual": 8000.0,
        "cuota_mensual": "S/ 20 (hasta S/ 5,000 ventas) o S/ 50 (hasta S/ 8,000 ventas)",
        "comprobantes": "Boletas de venta y tickets",
        "libros_contables": "Ninguno",
        "igv": "No paga IGV por separado (incluido en cuota fija)",
        "enlace": "https://www.gob.pe/8112-nuevo-regimen-unico-simplificado-nrus-actividades-no-comprendidas-en-el-nuevo-rus",
    },
    "RER": {
        "name": "Régimen Especial de Renta (RER)",
        "aplicable_a": "Personas Naturales y Personas Jurídicas",
        "limite_ventas_anual": 525000.0,
        "tasa_renta": "1.5% mensual de ingresos netos",
        "igv": "18%",
        "comprobantes": "Facturas, Boletas y notas",
        "libros_contables": "Registro de Compras y Registro de Ventas",
        "enlace": "https://www.gob.pe/6989-regimen-especial-de-renta-rer",
    },
    "RMT": {
        "name": "Régimen MYPE Tributario (RMT)",
        "aplicable_a": "Personas Naturales y Personas Jurídicas",
        "limite_ventas_anual_uit": 1700,
        "tasa_renta": "1% pago a cuenta mensual (hasta 300 UIT)",
        "igv": "18%",
        "comprobantes": "Facturas, Boletas y todos los comprobantes permitidos",
        "libros_contables": "Compras, Ventas y Diario Simplificado (hasta 300 UIT)",
        "enlace": "https://www.gob.pe/6990-regimen-mype-tributario-rmt",
    },
    "RG": {
        "name": "Régimen General (RG)",
        "aplicable_a": "Personas Naturales y Personas Jurídicas sin tope de ventas",
        "limite_ventas_anual": "Sin límite",
        "tasa_renta": "1.5% a cuenta mensual y 29.5% anual sobre utilidad neta",
        "igv": "18%",
        "comprobantes": "Todos",
        "libros_contables": "Contabilidad completa si supera 1700 UIT",
        "enlace": "https://www.gob.pe/6991-regimen-general-de-renta",
    },
}

# Actividades no permitidas o con condiciones especiales en PNTE
RESTRICTED_ACTIVITIES: List[Dict[str, Any]] = [
    {
        "keywords": ["seguro", "seguros", "reaseguros", "financiera", "banco", "caja"],
        "permitido_pnte": False,
        "motivo": "Requiere autorización previa de la SBS y solo bajo forma de S.A. (Ley 26702).",
    },
    {
        "keywords": ["saneamiento", "agua potable", "desagüe", "alcantarillado"],
        "permitido_pnte": False,
        "motivo": "Requiere autorización previa de SUNASS y objeto social exclusivo (Ley 26338).",
    },
    {
        "keywords": ["universidad", "universitari", "educacion superior", "maestria", "doctorado", "posgrado"],
        "permitido_pnte": False,
        "motivo": "Requiere autorización y licenciamiento previo de SUNEDU (Ley 30220).",
    },
    {
        "keywords": ["instituto", "escuela tecnica"],
        "permitido_pnte": True,
        "condicion": "Requiere autorización previa del Ministerio de Educación (MINEDU).",
    },
    {
        "keywords": ["vigilancia", "seguridad privada", "intermediacion laboral", "limpieza"],
        "permitido_pnte": False,
        "motivo": "Requiere un capital social mínimo de 45 UIT (Ley 27626).",
    },
    {
        "keywords": ["transporte de valores", "caudales"],
        "permitido_pnte": False,
        "motivo": "Requiere autorización previa de la SBS y Mininter.",
    },
    {
        "keywords": ["auditoria contable", "auditorias contables"],
        "permitido_pnte": True,
        "condicion": "No se puede constituir como EIRL. Requiere al menos un socio Contador Público Colegiado.",
    },
]

# Sedes y Centros de Desarrollo Empresarial (CDE) del PNTE
PNTE_SEDES: Dict[str, Dict[str, str]] = {
    "lima": {
        "direccion": "Calle Uno Oeste 060, San Isidro / Centros MAC en Lima y Callao",
        "horario": "Lunes a Viernes 8:30 am - 5:00 pm",
        "contacto": "016162291 anexo 1",
    },
    "arequipa": {
        "direccion": "Centro MAC Arequipa - Mall Aventura Porongoche",
        "horario": "Lunes a Viernes 8:30 am - 4:30 pm",
        "contacto": "tuempresa@produce.gob.pe",
    },
    "piura": {
        "direccion": "Centro MAC Piura - Real Plaza Piura",
        "horario": "Lunes a Viernes 8:30 am - 4:30 pm",
        "contacto": "tuempresa@produce.gob.pe",
    },
    "la libertad": {
        "direccion": "Centro MAC La Libertad - Mallplaza Trujillo",
        "horario": "Lunes a Viernes 8:30 am - 4:30 pm",
        "contacto": "tuempresa@produce.gob.pe",
    },
    "cusco": {
        "direccion": "Centro MAC Cusco - C.C. Real Plaza Cusco",
        "horario": "Lunes a Viernes 8:30 am - 4:30 pm",
        "contacto": "tuempresa@produce.gob.pe",
    },
}

# Redes Sociales y Enlaces Oficiales
OFFICIAL_LINKS = {
    "web_general": "www.gob.pe/tuempresa",
    "sedes": "www.gob.pe/institucion/tuempresa/sedes",
    "contacto_tel": "016162291",
    "contacto_email": "tuempresa@produce.gob.pe",
    "sacs": "https://www.gob.pe/26692-constituir-tu-empresa-como-sociedad-por-acciones-cerradas-simplificadas-sacs",
    "facebook": "https://facebook.com/tuempresagobpe",
    "instagram": "@tuempresagobpe",
    "tiktok": "https://www.tiktok.com/@tuempresagobpe",
    "linkedin": "https://www.linkedin.com/company/tuempresa/",
    "twitter": "@tuempresagobpe",
}

# Pasos oficiales del proceso de constitución
CONSTITUTION_STEPS = [
    "1. Diagnóstico y asesoría gratuita en el PNTE.",
    "2. Búsqueda y Reserva de nombre en SUNARP (gratuito mediante PNTE).",
    "3. Elaboración del Acto Constitutivo (Minuta) gratuita.",
    "4. Pago y firma de Escritura Pública en Notaría con tarifa social.",
    "5. Inscripción en SUNARP (RUC inactivo otorgado).",
    "6. Activación de RUC con Clave SOL en SUNAT y elección de régimen.",
]

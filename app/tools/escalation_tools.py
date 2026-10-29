"""Herramientas de escalamiento a asesores humanos del PNTE."""

from typing import Dict, Any
from app.services.db_service import create_advisor_ticket, save_user


async def register_advisor_ticket_tool(
    user_id: str,
    document_number: str,
    name: str,
    phone: str,
    details: str,
) -> Dict[str, Any]:
    """Registra una solicitud de atención personalizada con un asesor del PNTE."""
    await save_user(
        user_id=user_id,
        name=name,
        document_number=document_number,
        phone=phone,
    )
    ticket_id = await create_advisor_ticket(
        user_id=user_id,
        document_number=document_number,
        name=name,
        phone=phone,
        details=details,
    )
    return {
        "success": True,
        "ticket_id": ticket_id,
        "summary": "Un asesor empresarial del PNTE se pondrá en contacto contigo a la brevedad.",
    }

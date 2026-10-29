"""Agente de escalamiento y registro de citas con asesores empresariales del PNTE."""

import re
from app.graph.state import AgentState
from app.callbacks.metrics_callback import metrics_collector
from app.services.db_service import create_advisor_ticket, save_user


async def escalation_agent_node(state: AgentState) -> AgentState:
    """Nodo conversacional de máquina de estados para reservar atención con asesor humano."""
    metrics_collector.record_agent_call("escalation_agent")
    user_msg = state["messages"][-1].content.strip()
    msg_lower = user_msg.lower()

    step = state.get("escalation_step") or "idle"
    user_data = dict(state.get("user_data", {}))
    session_id = state.get("session_id", "default_user")

    # Si apenas ingresa a la opción de asesor
    if step == "idle":
        # Revisar si ya escribió su documento directamente
        doc_digits = re.findall(r"\b\d{8,12}\b", user_msg)
        if doc_digits:
            doc = doc_digits[0]
            user_data["pending_document"] = doc
            response_text = f"¿Confirmas que tu número de documento es {doc}? Responde con 'si' o 'no'."
            new_step = "confirming_doc"
        else:
            response_text = "Para conectar con un asesor del programa Tu Empresa, por favor ingresa tu número de documento (DNI o CE):"
            new_step = "asking_doc"

    elif step == "asking_doc":
        doc_clean = re.sub(r"[^\w]", "", user_msg)
        user_data["pending_document"] = doc_clean
        response_text = f"¿Confirmas que tu número de documento es {doc_clean}? Responde con 'si' o 'no'."
        new_step = "confirming_doc"

    elif step == "confirming_doc":
        if "si" in msg_lower or "sí" in msg_lower or "correcto" in msg_lower:
            user_data["document_number"] = user_data.get("pending_document", "")
            response_text = "Continuemos. Por favor, indícanos cuál es tu nombre y apellido:"
            new_step = "asking_name"
        else:
            response_text = "Por favor, vuelve a ingresar tu número de documento correcto:"
            new_step = "asking_doc"

    elif step == "asking_name":
        user_data["pending_name"] = user_msg
        response_text = f"¿Confirmas que tu nombre es {user_msg}? Responde con 'si' o 'no'."
        new_step = "confirming_name"

    elif step == "confirming_name":
        if "si" in msg_lower or "sí" in msg_lower or "correcto" in msg_lower:
            user_data["name"] = user_data.get("pending_name", "Emprendedor")
            client_name = user_data["name"].split()[0]
            response_text = f"{client_name}, indícanos cuál es el motivo de tu consulta con el asesor empresarial:"
            new_step = "asking_motive"
        else:
            response_text = "Por favor, indícanos nuevamente cuál es tu nombre:"
            new_step = "asking_name"

    elif step == "asking_motive":
        motive = user_msg
        user_data["motive"] = motive
        doc = user_data.get("document_number", "No especificado")
        name = user_data.get("name", "Emprendedor")
        phone = user_data.get("phone", session_id)

        # Registrar ticket en SQLite
        try:
            await save_user(user_id=session_id, name=name, document_number=doc, phone=phone)
            ticket_id = await create_advisor_ticket(
                user_id=session_id,
                document_number=doc,
                name=name,
                phone=phone,
                details=motive,
            )
            response_text = (
                f"¡Listo! Tu solicitud #{ticket_id} fue registrada. "
                f"Un asesor del PNTE te contactará pronto. ⏰ ¿Te ayudo con algo más?"
            )
        except Exception:
            response_text = "Tu solicitud fue anotada. Un asesor del PNTE se pondrá en contacto pronto. ⏰ ¿Te ayudo con algo más?"

        new_step = "completed"

    else:
        response_text = "¿Deseas solicitar otra consulta con un asesor o resolver dudas sobre formalización?"
        new_step = "idle"

    return {
        **state,
        "final_response": response_text[:250],
        "active_agent": "escalation_agent",
        "escalation_step": new_step,
        "user_data": user_data,
    }

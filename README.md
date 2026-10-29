# Asistente Virtual Multiagente del PNTE (Programa Nacional Tu Empresa)

Sistema de inteligencia artificial multiagente desarrollado con **LangGraph**, **FastAPI**, **Guardrails** y **Callbacks** para brindar orientación 24/7 sobre la formalización y constitución de empresas a unidades productivas y emprendedores del Perú.

El sistema reemplaza la arquitectura de chatbot monolítico previa por un grafo de agentes especializados que razonan, delegan y ejecutan herramientas de dominio con límites estrictos de alcance y longitud (≤ 250 caracteres por respuesta).

---

## 🏛️ Ámbito y Dominio Oficial

- **Programa**: Programa Nacional Tu Empresa (PNTE) - Ministerio de la Producción (PRODUCE), Perú.
- **Enfoque Exclusivo**: Formalización y constitución de empresas (EIRL, SRL, SAC, SA, SACS y Persona Natural con Negocio).
- **Trámites en PNTE**: Asesoría gratuita, Reserva de nombre SUNARP gratuita, Elaboración de Acto Constitutivo (Minuta) gratuita, Notarías con convenio desde S/ 120, y exención registral si el capital es ≤ 1 UIT (S/ 5,350 en 2025).
- **Límite Canónico**: Consultas ajenas reciben inmediatamente:
  > *"Solo puedo ayudarte con formalización y constitución de empresas. ¿Te ayudo en algo más?"*

---

## 🤖 Arquitectura Multiagente (LangGraph)

El flujo está coordinado mediante un **`StateGraph`** con memoria conversacional (`MemorySaver` por `thread_id` / `session_id`):

```
                        ┌────────────────────────┐
                        │    Cliente / Frontend  │
                        │    (Web, Apps, APIs)   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   FastAPI Endpoints    │
                        │  /api/v1/chat          │
                        │  /api/v1/chat/stream   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │    Input Guardrails    │
                        │  - Filtro inyección    │
                        │  - Detección alcance   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │    Supervisor Node     │
                        │  (Orquestador/Router)  │
                        └─────┬──┬──┬──┬──┬──────┘
                              │  │  │  │  │
      ┌───────────────────────┘  │  │  │  └──────────────────────┐
      ▼                          ▼  │  ▼                         ▼
┌──────────────┐   ┌──────────────┐ │ ┌──────────────┐   ┌──────────────┐
│ Greeting     │   │Formalization │ │ │  Cost Agent  │   │ Escalation   │
│ Agent        │   │ Agent        │ │ │(Tarifas, UIT,│   │ Agent        │
│(Menú y Hola) │   │(SAC,EIRL,etc)│ │ │ Sedes PNTE)  │   │(Agendar cita)│
└──────┬───────┘   └──────┬───────┘ │ └──────┬───────┘   └──────┬───────┘
       │                  │         ▼        │                  │
       │                  │  ┌──────────────┐│                  │
       │                  │  │  Tax Agent   ││                  │
       │                  │  │(NRUS,RER,RMT)││                  │
       │                  │  └──────┬───────┘│                  │
       │                  │         │        │                  │
       └──────────────────┴─────────┼────────┴──────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   Guardrail de Salida  │
                        │  - Límite ≤ 250 chars  │
                        │  - Tono y limpieza     │
                        │  - Fallback canónico   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │    Métricas Callback   │
                        │  (Latencia y tokens)   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │  Respuesta al Usuario  │
                        └────────────────────────┘
```

### Agentes Especializados
1. **Supervisor / Router Agent**: Clasifica la intención del usuario y delega al nodo correspondiente, o redirige a guardrails si detecta consultas fuera de ámbito.
2. **Formalization Agent**: Especialista en tipos de personas jurídicas (EIRL, SRL, SAC, SACS), personas naturales con negocio, requisitos de constitución, reserva de nombre y validación de actividades restringidas (SBS, SUNEDU, MINEDU).
3. **Tax Agent**: Especialista en los regímenes tributarios peruanos (NRUS, RER, RMT, Régimen General), límites de ventas, tasas, comprobantes permitidos y libros contables.
4. **Cost Agent**: Especialista en tarifas notariales sociales (desde S/ 120), evaluación de tope de 1 UIT (S/ 5,350) para gratuidad de derechos registrales, y directorio de sedes/CDE del PNTE.
5. **Escalation Agent**: Máquina de estados conversacional que recopila y confirma datos (DNI/CE, Nombre completo, Motivo) para registrar una solicitud formal de contacto con un asesor empresarial de carne y hueso.
6. **Guardrail Node**: Garantiza que el 100% de las respuestas no superen los 250 caracteres, preservando la cordialidad, claridad y directiva oficial.

---

## 🚀 Instalación y Ejecución

### 1. Clonar y configurar entorno
```bash
git clone <repo-url>
cd pnte-bot

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o en Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y configura tu clave de OpenAI:
```bash
cp .env.example .env
```
Edita `.env`:
```ini
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
MAX_RESPONSE_CHARS=250
UIT_VALUE=5350
DATABASE_URL=sqlite+aiosqlite:///./pnte_database.db
```

### 3. Iniciar el servidor FastAPI
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
La documentación interactiva Swagger estará disponible de inmediato en:
👉 `http://localhost:8000/docs`

---

## 📡 Endpoints de la API

### 1. Chat síncrono
- **Ruta**: `POST /api/v1/chat`
- **Request Body**:
```json
{
  "session_id": "sesion-usuario-123",
  "message": "¿Cuáles son los requisitos para crear una SAC?",
  "phone": "999888777",
  "channel": "web"
}
```
- **Response (200 OK)**:
```json
{
  "session_id": "sesion-usuario-123",
  "response": "Requisitos PNTE: 1 a 5 opciones de nombre, DNI vigente de socios/titular, objeto social detallado, capital social (mín. S/ 1) y declaración jurada.",
  "agent_used": "formalization_agent",
  "character_count": 164,
  "guardrails_applied": [],
  "escalation_step": "idle",
  "latency_ms": 12.4
}
```

### 2. Chat con Streaming en tiempo real (SSE)
- **Ruta**: `POST /api/v1/chat/stream`
- Emite eventos estándar `text/event-stream` con chunks progresivos y `data: [DONE]` al terminar.

### 3. Listar solicitudes para asesores humanos
- **Ruta**: `GET /api/v1/advisor-requests?limit=20`
- Retorna las consultas agendadas por usuarios que solicitaron hablar con un asesor (DNI, Nombre, Teléfono, Motivo, Estado).

### 4. Métricas de observabilidad y rendimiento
- **Ruta**: `GET /api/v1/metrics`
- Retorna total de peticiones, llamadas por agente, latencia promedio y tokens consumidos.

### 5. Health Check
- **Ruta**: `GET /api/v1/health`

---

## 🧪 Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración que cubre:
- Cumplimiento de guardrails (límite ≤ 250 caracteres, rechazo a temas ajenos).
- Detección de inyección de instrucciones.
- Recomendación de regímenes tributarios y costos con UIT.
- Flujo de interacción turn-by-turn con el agente de escalamiento.
- Endpoints HTTP y streaming de FastAPI.

Para ejecutar los tests:
```bash
pytest tests/ -v
```

---

## 🐳 Despliegue con Docker

Para construir y levantar el contenedor:
```bash
docker build -t pnte-assistant:latest .
docker run -p 8000:8000 --env-file .env pnte-assistant:latest
```

---

## 📚 Estructura del Proyecto

```
pnte-bot/
├── app/
│   ├── api/
│   │   ├── routes.py               # Endpoints REST y Streaming (FastAPI)
│   │   └── schemas.py              # Validación tipada con Pydantic
│   ├── agents/
│   │   ├── supervisor.py           # Enrutador inteligente de intenciones
│   │   ├── formalization_agent.py  # Agente legal / tipos societarios
│   │   ├── tax_agent.py            # Agente tributario (NRUS/RER/RMT/RG)
│   │   ├── cost_agent.py           # Agente de costos notariales y sedes
│   │   ├── escalation_agent.py     # Agente para agendar con asesor humano
│   │   ├── greeting_agent.py       # Agente de saludo y opciones
│   │   └── guardrail_node.py       # Guardrail de salida y sanitización
│   ├── callbacks/
│   │   └── metrics_callback.py     # Observabilidad de latencia y tokens
│   ├── core/
│   │   ├── llm.py                  # Fábrica y configuración de OpenAI
│   │   └── logging.py              # Logger estructurado
│   ├── data/
│   │   └── pnte_knowledge.py       # Conocimiento canónico del PNTE
│   ├── graph/
│   │   ├── state.py                # Definición del AgentState
│   │   └── workflow.py             # Grafo compilado StateGraph con memoria
│   ├── guardrails/
│   │   ├── input_guardrails.py     # Filtro de seguridad y alcance
│   │   └── output_guardrails.py    # Podado estricto ≤ 250 caracteres
│   ├── services/
│   │   ├── chat_service.py         # Orquestación de ejecuciones y streaming
│   │   └── db_service.py           # Persistencia en SQLite
│   ├── tools/
│   │   ├── kb_tools.py             # Herramientas de búsqueda y actividades
│   │   ├── tax_tools.py            # Herramientas de cálculo tributario
│   │   ├── cost_tools.py           # Herramientas de costos y sedes CDE
│   │   └── escalation_tools.py     # Herramientas de tickets con asesores
│   ├── utils/
│   │   └── text.py                 # Normalización de tildes y caracteres
│   ├── config.py                   # Pydantic Settings
│   └── main.py                     # Entrypoint de FastAPI
├── tests/                          # Suite de pruebas unitarias e integración
├── .env.example                    # Plantilla de variables de entorno
├── Dockerfile                      # Imagen para despliegue en contenedores
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Documentación técnica
```

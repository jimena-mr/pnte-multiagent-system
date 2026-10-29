"""Script de demostración interactiva por consola para el asistente multiagente del PNTE."""

import asyncio
from app.services.chat_service import process_chat_message
from app.services.db_service import init_db


async def main():
    await init_db()
    session_id = "demo_console_session"
    print("\n" + "=" * 60)
    print("🤖 BIENVENIDO AL ASISTENTE MULTIAGENTE PNTE (CONSOLA DEMO)")
    print("Escribe tus consultas de formalización o 'salir' para terminar.")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("👤 Tú: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("¡Hasta pronto!")
                break

            result = await process_chat_message(session_id=session_id, message=user_input)
            agent = result["agent_used"]
            chars = result["character_count"]
            latency = result["latency_ms"]

            print(f"\n🤖 [{agent} | {chars} chars | {latency}ms]:")
            print(f"👉 {result['response']}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nSesión finalizada.")
            break


if __name__ == "__main__":
    asyncio.run(main())

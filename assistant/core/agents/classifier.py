from langchain_google_genai import ChatGoogleGenerativeAI

from assistant.settings import UBE_PROVIDER_ID
from core.utils.gemini_client import get_gemini_client_args
from core.agents.chat_agent import get_chat_agent
from core.agents.faq_agent import get_faq_agent
from core.agents.public_agent import get_public_agent
from core.agents.soporte_ti__agent import get_soporte_ti_agent
from core.agents.ventas_agent import get_ventas_agent
from core.models import Provider
from core.utils.memory_manager import memoria_manager
import logging


logger = logging.getLogger(__name__)

async def classify_query(user_message: str) -> str:
    """Clasifica la pregunta usando Gemini"""
    from assistant.settings import GEMINI_API_KEY

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        client_args=get_gemini_client_args(),
    )

    prompt = f"""
    Clasifica esta pregunta en UNA categoría:

    Categorías:
    - ventas: Carreras, matriculacion, grupos, grupos disponibles, requisitos, malla curricular, precios de carreras
    - faq: Biblioteca, credenciales, correo, horarios
    - soporte_ti: contraseña, credenciales SGA, correo, email
    - public: beneficios, quienes somos, mision, vision, informacion general de la UBE, contactos, becas, ayuda financiera, link SGA, link pagina web, plataforma virtual

    Pregunta: "{user_message}"

    Responde SOLO con la palabra: "ventas", "faq", "soporte_ti", "public"
    """

    response = await llm.ainvoke(prompt)
    category = response.content.strip().lower()
    print(f"CATEGORIA: {category}")
    return category

async def route_message(
    chat_id: int,
    user_message: str,
    token: str,
    provider: Provider
):
    """Enruta el mensaje al agente correcto manteniendo contexto"""

    try:
        category = await classify_query(user_message)
        print(provider.id)

        if provider.id == UBE_PROVIDER_ID:
            agent_map = {
                "faq": lambda: get_faq_agent(chat_id),
                "soporte_ti": lambda: get_soporte_ti_agent(chat_id, token),
                "public": lambda: get_public_agent(chat_id),
                "ventas": lambda: get_ventas_agent(chat_id),
            }
        else:
            agent_map = {
                "ventas": lambda: get_ventas_agent(chat_id),
                "public": lambda: get_public_agent(chat_id),
            }

        agent = agent_map.get(category, lambda: get_chat_agent(chat_id))()
        response = await agent.ainvoke({"input": user_message})

        logger.info(f"Invocando agente | Contexto existente: {memoria_manager.get_size()} chats")

        ai_response = response.get("output", "Ocurrió un error procesando tu solicitud.")
        logger.info(f"Respuesta generada | chat_id: {chat_id}")

        return category, ai_response

    except RuntimeError as e:
        if "shutdown" in str(e).lower() or "cannot schedule new futures" in str(e):
            logger.warning(f"Servidor recargado durante la petición: {e}")
            return "error", "El servidor se reinició. Por favor envía el mensaje de nuevo."
        raise
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
            logger.warning(f"Cuota Gemini agotada: {e}")
            return "error", "Límite de uso de la IA alcanzado. Espera unos minutos o revisa tu plan en Google AI Studio."
        logger.error(f"Error en route_message: {e}", exc_info=True)
        return "error", "Ocurrió un error. Intenta de nuevo."
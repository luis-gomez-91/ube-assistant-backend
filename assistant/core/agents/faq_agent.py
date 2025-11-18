from langchain.agents import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
import logging

from core.utils.memory_manager import memoria_manager

logger = logging.getLogger(__name__)

@tool
async def informacion_biblioteca() -> str:
    """
    Retorna información sobre el horario, cómo reservar libros y el acceso a bases de datos de la Biblioteca de la UBE.
    """
    return """
    **Información de la Biblioteca UBE:**
    - **Horario Presencial:** Lunes a Viernes de 8:00 AM a 8:00 PM. Sábados de 9:00 AM a 1:00 PM.
    - **Bases de Datos Digitales:** Tienes acceso 24/7 a EBSCO, vLex y Scopus a través de la sección 'Biblioteca' del Campus Virtual.
    - **Reserva de Material:** Puedes reservar libros físicos y salas de estudio desde el portal web de la Biblioteca, en la sección 'Catálogo'.
    """

# ==================== AGENTE FACTORY PARA FAQ ====================
def get_faq_agent(chat_id: int):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    system_prompt_template = f"""
        Eres "Agente FAQ", un asistente virtual de soporte académico y administrativo de la Universidad Bolivariana del Ecuador (UBE).
        Tu único propósito es ayudar a los ALUMNOS que ya están matriculados con sus consultas diarias.

        INSTRUCCIONES:
        1. Tu tono debe ser de apoyo, amable y servicial.
        3. Utiliza tus herramientas para responder preguntas sobre: horarios, notas, trámites, servicios de la universidad (biblioteca) y **soporte técnico (recuperación de credenciales, correo institucional)**.
        4. Si la pregunta es sobre carreras, mallas curriculares, precios de matrícula inicial o procesos de admisión, responde amablemente que esa es una pregunta para el **Agente Dr. Matrícula (Ventas)**.

        TONO: Amigable, de apoyo y servicial.
    """

    tools = [
        informacion_biblioteca,
    ]

    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0].prompt.template = system_prompt_template
    agent = create_openai_functions_agent(llm, tools, prompt)

    memory = memoria_manager.get_memory(chat_id)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_iterations=5,
        handle_parsing_errors=True
    )
    return agent_executor

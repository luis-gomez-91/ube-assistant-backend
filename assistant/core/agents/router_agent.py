import nest_asyncio
nest_asyncio.apply()

from core.agents.faq_agent import get_faq_agent
from langchain.agents import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
from langchain.memory import ConversationBufferMemory

# Importamos las factorías de agentes
from core.agents.ventas_agent2 import get_agent as get_ventas_agent

# Diccionario para almacenar la memoria de la conversación del Router
router_memorias = {}

# ==================== HERRAMIENTAS DEL ROUTER ====================
@tool
async def route_to_ventas(query: str, chat_id: int) -> str:
    """
    Úsese para preguntas sobre:
    - Carreras, postgrados, maestrías
    - Malla curricular, pensum de estudios, materias o asignaturas
    - Precios, costos, matrículas iniciales, grupos disponibles
    - Requisitos de admisión y proceso de matriculación

    Args:
        query: La consulta original del usuario.
        user_id: El identificador del usuario.
    """
    print(f"CHAT ID: {chat_id}")
    ventas_agent = get_ventas_agent(chat_id)
    return await ventas_agent.ainvoke({"input": query})['output']


@tool
async def route_to_faq(query: str, user_id: str) -> str:
    """
    Úsese para preguntas sobre:
    - Horarios, notas, calificaciones
    - Trámites internos (certificados, retiros de materias, solicitudes)
    - Servicios para estudiantes (biblioteca, campus virtual, calendarios académicos)
    - Becas internas o ayudas estudiantiles

    Args:
        query: La consulta original del usuario.
        user_id: El identificador del usuario.
    """
    faq_agent = get_faq_agent(user_id)
    return await faq_agent.ainvoke({"input": query})['output']


# Lista de herramientas para el Agente Router
tools = [route_to_ventas, route_to_faq]


# ==================== AGENTE FACTORY PARA EL ROUTER ====================
def get_router_agent(chat_id: int):
    print(f"CHAT ID ROUTER AGENT: {chat_id}")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    system_prompt_template = """
        Eres el **Agente Router Principal** de la Universidad Bolivariana del Ecuador (UBE).
        Tu única función es CLASIFICAR la intención del usuario y dirigir la consulta al agente especializado correcto.

        REGLAS DE CLASIFICACIÓN:
        1. **Si el usuario pregunta por información de ADMISIÓN, VENTAS o CARRERAS (malla, precio, matrícula, grupos), usa la herramienta `route_to_ventas`.**
        2. **Si el usuario pregunta por servicios para ALUMNOS MATRICULADOS (horarios, notas, trámites internos), usa la herramienta `route_to_faq`.**
        3. Siempre debes llamar a UNA de las dos herramientas, pasando la consulta original y el ID de usuario. No intentes responder tú mismo.

        TONO: Neutro y analítico (ya que tu respuesta final la dará el agente especializado).
    """

    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0].prompt.template = system_prompt_template
    agent = create_openai_functions_agent(llm, tools, prompt)

    # if chat_id in memorias:
    #     memory = deepcopy(memorias[chat_id])
    # else:
    #     memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    #     memorias[chat_id] = memory

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        # memory=memory,
        max_iterations=5,
        handle_parsing_errors=True
    )

    return agent_executor

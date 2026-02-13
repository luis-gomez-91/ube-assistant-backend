from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_classic import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
import logging

from core.utils.gemini_client import get_gemini_client_args
from core.utils.memory_manager import memoria_manager

logger = logging.getLogger(__name__)

# @tool
# async def default() -> str:
#     """
#     Chat.
#     """
#     return """
#     Retorna
#     """

@tool
async def default_tool() -> str:
    """
    Skill por defecto que responde cuando el usuario hace consultas
    fuera del alcance definido.
    """
    return (
        "No puedo resolver preguntas como operaciones matemáticas u otros temas externos. "
        "Si deseas más información puedes comunicarte por:\n"
        "- 📲 WhatsApp: https://api.whatsapp.com/send/?phone=593989758382&text=Me+gustar%C3%ADa+saber+informaci%C3%B3n+sobre+las+carreras&type=phone_number&app_absent=0\n"
        "- 🌐 Página oficial: https://ube.edu.ec/"
    )

def get_chat_agent(chat_id: int):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        client_args=get_gemini_client_args(),
    )

    system_prompt_template = f"""
        Eres un asistente virtual de la Universidad Bolivariana del Ecuador (UBE).
        Tu propósitos sonÑ
        - Saludar
        - Chat de forma libre solo con temas relacionados a la universidad Bolivariana
        
        TONO: Amigable, de apoyo y servicial.
    """

    tools = [
        default_tool,
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

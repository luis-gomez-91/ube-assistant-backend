# core/ai/argo_agent.py
import argo
from argo import Message
from argo.skills import chat
from assistant.settings import GEMINI_API_KEY
# from core.services.ventas_service import fetch_carreras, fetch_grupos, fetch_malla
from core.services.ventas_service import fetch_carreras
# from utils import get_id_by_name, formatear_texto_carreras


def initialize_agent():
    if not GEMINI_API_KEY:
        raise ValueError("TOKEN environment variable not set.")

    llm = argo.LLM(
        model="google/gemini-2.5-flash",
        api_key=GEMINI_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        verbose=True,
    )

    agent = argo.ChatAgent(
        name="Dr. Matrícula",
        description="Asistente que brinda información de carreras de la UBE.",
        llm=llm,
        skills=[chat],
    )

    agent.system_prompt = """
        Eres un asistente llamado "Dr. Matrícula" que trabaja para la Universidad Bolivariana del Ecuador (UBE).
        Tu función es exclusivamente brindar información sobre:
        - Carreras de la UBE
        - Matrículas y requisitos
        - Mallas curriculares
        - Grupos disponibles
        - Procesos de admisión

        Cuando el usuario pregunte por grupos o mallas, identifica el nombre de la carrera en su mensaje
        y utiliza las herramientas correspondientes.

        Si no encuentras la información de una carrera específica, indícale que puede consultarla en la página oficial: https://sga.ube.edu.ec/.

        No eres un asistente general ni respondes a temas fuera de la UBE.
    """

    # Inicializar datos
    carreras_instance = fetch_carreras()
    agent.carreras = carreras_instance

    return agent

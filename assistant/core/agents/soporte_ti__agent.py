from core.agents.ventas_agent import memoria_manager
from core.services.faq_service import fetch_verify, password_recovery
from schemas.faq import VerifyModel, PasswordRecoveryModel
from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_classic import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
import logging

from core.utils.gemini_client import get_gemini_client_args


logger = logging.getLogger(__name__)
tokens = {}

def herramienta_token(token: str, chat_id: int):
    """
    Factory para crear la herramienta de correo institucional con el token ya incluido.
    """

    @tool
    async def recuperar_credenciales_sga(numero_celular: str | None = None) -> str:
        """
        Asiste al alumno con la recuperación de credenciales del Sistema de Gestión Académica (SGA).
        Si no se proporciona el número de celular, se solicita al usuario que lo indique.
        """
        if not numero_celular:
            return (
                "Necesito tu número de celular en formato 09xxxxxxxx para continuar con la recuperación de tu cuenta. "
                "Por favor, envíame tu número de WhatsApp registrado en el sistema."
            )

        data: PasswordRecoveryModel = await password_recovery(token, numero_celular)

        if data.error:
            return f"⚠️ No se pudo completar la recuperación de credenciales: {data.error}"

        if data.whatsapp_response:
            return (
                f"Perfecto ✅, tu número registrado es **{numero_celular}**.\n\n"
                f"{data.whatsapp_response}\n\n"
                "Si no recibes el mensaje en unos minutos, comunícate con Soporte Técnico."
            )

        if data.message:
            return data.message

    @tool
    async def informacion_correo_institucional() -> str:
        """
        Responde preguntas sobre cuál es el correo institucional, su formato o su uso.
        """
        try:
            user_instance: VerifyModel = await fetch_verify(token)
            correo = user_instance.email
            nombre = user_instance.name

            return f"""
            Tu correo institucional es: **{correo}**

            Hola {nombre}, es esencial que uses este correo para toda la comunicación académica y administrativa.

            **Usos principales:**
            - Acceso a herramientas de Google Workspace (Drive, Meet, Classroom).
            - Recepción de notificaciones oficiales y clases virtuales.
            - Acceso a bases de datos y servicios de biblioteca.
            - Comunicación con profesores y administrativos.

            Si no lo has activado, revisa tu correo personal con el que te matriculaste, allí se enviaron las instrucciones iniciales.
            """
        except Exception as e:
            logger.error(f"Error al recuperar correo institucional: {e}")
            return """
            No pudimos verificar tu correo institucional en este momento.

            Por favor:
            1. Verifica que tu token sea válido
            2. Contacta a la Dirección de Tecnologías de la Información (DTI) si el problema persiste.
            """

    return [informacion_correo_institucional, recuperar_credenciales_sga]


@tool
async def reestablecer_contrasena_correo() -> str:
    """
    Explica el proceso para reestablecer la contraseña del correo institucional (@ube.edu.ec).
    """
    return """
    El **restablecimiento de la contraseña de tu correo institucional** se gestiona a través de la plataforma de Google (Gmail):
    1.  Ve a la página de inicio de sesión de Gmail/Google.
    2.  Ingresa tu correo institucional completo (ejemplo@ube.edu.ec).
    3.  Haz clic en "**Olvidé mi contraseña**".
    4.  Si configuraste opciones de recuperación (teléfono o correo alternativo), síguelas.

    **Importante:** Si no puedes reestablecerla, debes contactar a la Dirección de Tecnologías de la Información (DTI) de la UBE para que realicen el reinicio manual por motivos de seguridad.
    """


def get_soporte_ti_agent(chat_id: int, token: str):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        client_args=get_gemini_client_args(),
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

    herramientas_con_token = herramienta_token(token, chat_id)

    tools = [
        reestablecer_contrasena_correo,
        *herramientas_con_token
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

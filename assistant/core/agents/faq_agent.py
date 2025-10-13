import nest_asyncio

nest_asyncio.apply()
from langchain.agents import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
from threading import Lock
from langchain.memory import ConversationBufferMemory
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
memorias = {}


# ==================== HERRAMIENTAS ESPECÍFICAS DEL AGENTE FAQ ====================

@tool
async def consultar_horarios(user_id: str) -> str:
    """
    Se activa cuando un alumno consulta sus horarios de clases o el calendario académico.
    Retorna el horario detallado de un estudiante activo.

    Args:
        user_id: Identificador único del alumno (se usa para buscar su información personal).
    """
    # Simulando una búsqueda en la base de datos de alumnos
    if user_id.lower() == 'lagomezv':
        return f"""
        ¡Hola, {user_id}! Tu horario actual es el siguiente:
        - Lunes: DERECHO CONSTITUCIONAL (8:00 AM - 10:00 AM) - Aula Virtual B-3
        - Martes: FILOSOFÍA DEL DERECHO (10:00 AM - 12:00 PM) - Aula B-5
        - Miércoles: DERECHO CIVIL: PERSONAS (7:00 PM - 9:00 PM) - Sesión Online Zoom
        - Jueves: CONSULTORÍA JURÍDICA (1:00 PM - 3:00 PM) - Laboratorio Práctico 1
        - Viernes: RECUPERACIÓN / TUTORÍAS (Horario Flexible)
        Recuerda revisar el Campus Virtual para cualquier actualización de última hora.
        """
    else:
        return "Lo siento, para consultar tu horario personal, necesito que accedas al sistema con tu usuario o proporciones un identificador válido."


@tool
async def consultar_notas(user_id: str, asignatura: str = None) -> str:
    """
    Muestra las calificaciones finales o parciales de un estudiante.

    Args:
        user_id: Identificador único del alumno.
        asignatura: Nombre opcional de la asignatura a consultar.
    """
    if user_id.lower() == 'lagomezv':
        if asignatura:
            return f"Tu calificación actual para '{asignatura}' es de 8.5/10.0 (Parcial 1). ¡Sigue esforzándote!"
        else:
            return f"""
            ¡{user_id}! Tus calificaciones del primer parcial son:
            - DERECHO CONSTITUCIONAL: 8.5/10.0
            - FILOSOFÍA DEL DERECHO: 9.2/10.0
            - DERECHO CIVIL: PERSONAS: 7.8/10.0
            - CONSULTORÍA JURÍDICA: 9.5/10.0
            Si necesitas el detalle completo, usa la opción del Campus Virtual.
            """
    return "No pude encontrar tus notas. Asegúrate de estar matriculado y de haber iniciado sesión correctamente."


@tool
async def procedimiento_tramite(nombre_tramite: str) -> str:
    """
    Explica los pasos para realizar trámites comunes (ej: solicitud de certificado, retiro de materia, justificación de inasistencia, solicitud de beca interna).

    Args:
        nombre_tramite: El nombre del trámite que el alumno desea realizar.
    """
    nombre_tramite = nombre_tramite.lower().strip()

    if "certificado" in nombre_tramite:
        return """
        Para la **Solicitud de Certificado de Matrícula/Notas**, sigue estos pasos:
        1. Accede al Campus Virtual (SGA) con tus credenciales.
        2. Ve a la sección 'Trámites' o 'Secretaría Virtual'.
        3. Selecciona el tipo de certificado que necesitas.
        4. Llena el formulario y realiza el pago del arancel (si aplica).
        5. El certificado estará disponible en formato digital en 48 horas.
        """
    elif "retiro" in nombre_tramite:
        return """
        Para el **Retiro de una Materia**, debes:
        1. Contactar a tu Tutor de Carrera.
        2. Llenar el 'Formulario de Solicitud de Retiro de Asignatura' en la Secretaría Virtual.
        3. La solicitud será evaluada por la Comisión Académica.
        4. Ten en cuenta las fechas límite establecidas en el calendario académico para evitar penalizaciones.
        """
    else:
        return "No conozco el procedimiento para ese trámite. Los trámites comunes que manejo son: Certificados, Retiro de materia y Solicitud de beca interna. ¿Cuál de ellos te interesa?"


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


@tool
async def recuperar_credenciales_sga() -> str:
    """
    Se activa cuando el alumno pregunta por cómo recuperar su usuario o contraseña
    del Sistema de Gestión Académica (SGA) o Campus Virtual.
    """
    return """
    Para **recuperar tu usuario y/o contraseña** del Sistema de Gestión Académica (SGA) / Campus Virtual:
    1.  Accede a la página de inicio de sesión del SGA.
    2.  Haz clic en el enlace "**¿Olvidó su contraseña?**" o "Recuperar credenciales".
    3.  Ingresa tu número de cédula o correo personal registrado.
    4.  Sigue las instrucciones enviadas a tu correo personal para crear una nueva contraseña.

    Si tienes problemas, comunícate con el área de Soporte Técnico para asistencia directa.
    """


@tool
async def informacion_correo_institucional(user_id: str) -> str:
    """
    Responde preguntas sobre cuál es el correo institucional, su formato o su uso.

    Args:
        user_id: El identificador del usuario.
    """
    formato = f"Tu correo institucional tiene el formato: **{user_id}@ube.edu.ec** (Ejemplo: lagomezv@ube.edu.ec)"

    return f"""
    Tu correo institucional es esencial para toda la comunicación académica y administrativa.
    {formato}

    Usos principales:
    - Acceso a herramientas de Google Workspace (Drive, Meet, Classroom).
    - Recepción de notificaciones oficiales y clases virtuales.
    - Acceso a bases de datos y servicios de biblioteca.

    Si no lo has activado, revisa tu correo personal con el que te matriculaste, allí se enviaron las instrucciones iniciales.
    """


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


# Lista de herramientas para el Agente FAQ
tools = [
    consultar_horarios,
    consultar_notas,
    procedimiento_tramite,
    informacion_biblioteca,
    recuperar_credenciales_sga,  # NUEVA
    informacion_correo_institucional,  # NUEVA
    reestablecer_contrasena_correo  # NUEVA
]


# ==================== AGENTE FACTORY PARA FAQ ====================
def get_faq_agent(user_id: str):
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
        2. Siempre que sea relevante, utiliza el 'user_id' proporcionado para personalizar la respuesta. El user_id actual es: {user_id}
        3. Utiliza tus herramientas para responder preguntas sobre: horarios, notas, trámites, servicios de la universidad (biblioteca) y **soporte técnico (recuperación de credenciales, correo institucional)**.
        4. Si la pregunta es sobre carreras, mallas curriculares, precios de matrícula inicial o procesos de admisión, responde amablemente que esa es una pregunta para el **Agente Dr. Matrícula (Ventas)**.

        TONO: Amigable, de apoyo y servicial.
    """

    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0].prompt.template = system_prompt_template
    agent = create_openai_functions_agent(llm, tools, prompt)

    if user_id not in memorias:
        memorias[user_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memorias[user_id],
        max_iterations=5,
        handle_parsing_errors=True
    )
    return agent_executor

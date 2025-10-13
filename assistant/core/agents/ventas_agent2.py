from langchain.agents import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from assistant.settings import GEMINI_API_KEY
from core.services.ventas_service import fetch_carreras, fetch_grupos, fetch_malla, fetch_detalle_carrera
from core.utils.ventas_utils import formatear_texto_carreras, get_id_by_name
from schemas.ventas.carreras import CarrerasModel, CarreraDetalleModel
from threading import Lock
from datetime import datetime, timedelta
import logging
from langchain.memory import ConversationBufferMemory


logger = logging.getLogger(__name__)

class CarrerasManager:
    """Manager thread-safe con caché"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._carreras = None
                    cls._instance._last_fetch = None
                    cls._instance._cache_duration = timedelta(hours=1)
        return cls._instance

    async def get_carreras(self) -> CarrerasModel:
        """Obtiene carreras con caché de 1 hora"""
        now = datetime.now()

        # Cache hit
        if self._carreras and self._last_fetch:
            if now - self._last_fetch < self._cache_duration:
                return self._carreras

        # Cache miss - fetch new data
        with self._lock:
            try:
                self._carreras = await fetch_carreras()
                self._last_fetch = now
                logger.info("Carreras cache actualizado")
            except Exception as e:
                logger.error(f"Error fetching carreras: {e}")
                # Si falla, retorna cache viejo si existe
                if self._carreras:
                    logger.warning("Usando cache antiguo de carreras")
                    return self._carreras
                raise

        return self._carreras


carreras_manager = CarrerasManager()


@tool
async def listar_carreras() -> str:
    """
    Retorna un resumen completo o filtrado de las carreras de la Universidad Bolivariana del Ecuador (UBE).
    El filtro puede ser por nivel (grado, postgrado o maestría) o por área de interés (salud, tecnología, educación, negocios, etc.).

    Ejemplo de uso:
    - "Deseo información de las carreras"
    - "Quiero información de las carreras de grado"
    - "Qué maestrias ofrecen"
    """

    carreras: CarrerasModel = await carreras_manager.get_carreras()
    grado = formatear_texto_carreras(carreras.grado, "grado")
    postgrado = formatear_texto_carreras(carreras.postgrado, "postgrado")

    preguntas_sugeridas = """
    ¿Prefieres que te muestre únicamente las carreras de pregrado o las de postgrado?
    ¿Quieres conocer los requisitos de ingreso para una carrera en particular?
    ¿Te interesa saber la duración promedio de una carrera o una maestría?
    ¿Quieres ver cuáles carreras están disponibles en modalidad online, presencial o híbrida?
    ¿Prefieres que te organice las carreras por áreas como salud, tecnología, educación o negocios?
    ¿Quieres información sobre becas, descuentos o facilidades de pago?
    ¿Te interesa conocer las oportunidades laborales de una carrera específica?
    ¿Deseas que te muestre los grupos y fechas de inicio más cercanos?
    ¿Quieres que te sugiera carreras relacionadas a tus intereses?
    ¿Te gustaría comparar dos carreras para ver cuál se ajusta mejor a lo que buscas?
    """

    return f"""
    {grado}
    
    ---
    
    {postgrado}

    Preguntas sugeridas para continuar:
    {preguntas_sugeridas}
    """

# @tool(return_direct=True)
@tool
async def listar_detalle_carrera(nombre_carrera: str) -> str:
    """
    Retorna información detallada sobre una carrera específica.

    Incluye:
    - Nombre
    - Título de graduado
    - Sesiones o jornadas disponibles (matutina, nocturna, fines de semana, etc...)
    - Modalidades disponibles (presencial, online, hibrida, etc...)
    - Precios (inscripción, matrícula, cuotas y homologación)

    Si la carrera no existe, sugiere carreras similares accediendo a la tool listar_carreras.
    """
    carreras: CarrerasModel = await carreras_manager.get_carreras()
    id_carrera = get_id_by_name(carreras, nombre_carrera)
    detalle: CarreraDetalleModel = await fetch_detalle_carrera(id_carrera)

    lineas = [
        f"🎓 **Carrera:** {detalle.nombre}",
        f"📜 **Título de graduado:** {detalle.titulo}"
    ]

    if detalle.sesiones:
        lineas.append(f"🗓️ **Sesiones disponibles:** {', '.join(detalle.sesiones)}")
    if detalle.modalidades:
        lineas.append(f"🎯 **Modalidades disponibles:** {', '.join(detalle.modalidades)}")
    if detalle.precios:
        precios = detalle.precios
        precios_texto = []
        if precios.inscripcion:
            precios_texto.append(f"- Inscripción: ${precios.inscripcion:,.2f}")
        if precios.matricula:
            precios_texto.append(f"- Matrícula: ${precios.matricula:,.2f}")
        if precios.numero_cuotas:
            precios_texto.append(f"- Número de cuotas: {precios.numero_cuotas}")
        if precios.homologacion:
            precios_texto.append(f"- Homologación: ${precios.homologacion:,.2f}")
        if precios_texto:
            lineas.append("**💰 Precios:**\n" + "\n".join(precios_texto))

    print("\n".join(lineas))
    return "\n\n".join(lineas)

@tool
async def listar_malla(nombre_carrera: str) -> str:
    """
    Esta tool se activa cuando el usuario pregunta por la malla curricular de una carrera.
    Cada periodo es equivalente a un semestre academico.

    Ejemplo de uso:
    - "¿Cuál es la malla de la carrera de Derecho?"
    - "¿Dame las asignaturas de la carrera de Enfermeria?"
    - "¿Cuál es la pensum académico?"
    """
    carreras: CarrerasModel = await carreras_manager.get_carreras()
    id_carrera = get_id_by_name(carreras, nombre_carrera)

    malla_instance = await fetch_malla(id_carrera)
    malla = malla_instance.data

    if not malla:
        return "No hay malla disponible para esta carrera."

    result = f"La Malla curricular de la carrera es la siguiente:\n"

    for nivel in malla:
        result += f"\n## {nivel.nivel_malla}"
        result += f"\nLas asignaturas de este período son:"

        for asig in nivel.asignaturas:
            result += f"\n- {asig.asignatura} ({asig.horas} horas)"
            if asig.creditos is not None:
                result += f"\n  - Créditos: {asig.creditos}"
    result += "\n"

    preguntas_sugeridas = """
    ¿Quieres que te dé una descripción más detallada de alguna asignatura?
    ¿Deseas saber la duración total de la carrera?
    ¿Quieres que te muestre el perfil de egreso de esta carrera?
    ¿Quieres conocer en qué modalidades (presencial, online, híbrida) se ofrece esta carrera?
    ¿Quieres que te muestre las oportunidades laborales al finalizar la carrera?
    ¿Te interesa conocer los precios o facilidades de pago de esta carrera?
    """

    result += f"\nPreguntas sugeridas para continuar:\n{preguntas_sugeridas}"
    return result


@tool
async def listar_grupos(nombre_carrera: str) -> str:
    """
    Esta tool se activa cuando el usuario pregunta por:
    - Los grupos o cupos disponibles de una carrera específica.
    - Las modalidades de estudio de una carrera.
    - Los precios de una carrera.
    - La matrícula o inscripción en una carrera.

    Ejemplo de uso:
    - "¿Qué grupos hay para la carrera de Fisioterapia?"
    - "¿Qué modalidades tiene la carrera de Derecho?"
    - "¿Cuánto cuesta estudiar Psicología?"
    - "Quiero matricularme en Enfermería"
    """

    carreras: CarrerasModel = await carreras_manager.get_carreras()
    id_carrera = get_id_by_name(carreras, nombre_carrera)

    if not id_carrera:
        return "Lo siento, no encontré esa carrera en nuestra base de datos. ¿Podrías verificar si está bien escrita o puedo listarte todas las carreras disponibles?"

    grupos_instance = await fetch_grupos(id_carrera)
    grupos = grupos_instance.data

    if not grupos:
        return "No hay grupos disponibles que inicien clase proximamente."

    result = f"Los grupos disponibles son:"
    result = "\n".join(
        f"- Paralelo: {grupo.nombre}, Fecha de inicio de clases aproximado: {grupo.fecha_inicio}, Sesion: {grupo.sesion}, Modalidad: {grupo.modalidad}"
        for grupo in grupos
    )

    preguntas_sugeridas = """
    ¿Quieres que te muestre el proceso de matrícula paso a paso?
    ¿Deseas saber si hay facilidades de pago o becas disponibles?
    ¿Quieres comparar esta carrera con otra para ver precios y modalidades?
    ¿Quieres que te muestre las fechas exactas de inscripción?
    ¿Deseas información sobre requisitos para matricularte en esta carrera?
    """

    result += f"\n\nPreguntas sugeridas para continuar:\n{preguntas_sugeridas}"
    return result


@tool
async def requisitos_matriculacion(nombre_carrera: str = None) -> str:
    """
    Retorna los requisitos de matriculación en la UBE.
    Puede mostrar requisitos generales o específicos para una carrera en particular.

    Instrucción al agente:
    - Si el usuario pregunta sobre “requisitos” sin especificar carrera, llama la tool sin parámetros.
    """

    # Requisitos generales
    requisitos_generales = """
    **Requisitos generales para matriculación:**
    - 🪪 Copia de cédula de identidad o pasaporte.
    - 🗳️ Certificado de votación (para mayores de 18 años).
    - 🎓 Título de bachiller o acta de grado (apostillado si es extranjero).
    - 📄 Certificado de notas del colegio.
    - 🖼️ 2 fotografías tamaño carnet.
    - 💰 Pago de inscripción y matrícula según corresponda.
    """

    # Obtener todas las carreras
    carreras = await carreras_manager.get_carreras()

    # Normalizamos la lista de carreras (grados + postgrados)
    todas_carreras = []
    todas_carreras.extend(carreras.grado)
    todas_carreras.extend(carreras.postgrado)

    if nombre_carrera:
        id_carrera = get_id_by_name(carreras.data, nombre_carrera)
        if not id_carrera:
            return f"No encontré la carrera '{nombre_carrera}'. ¿Quieres que te muestre los requisitos generales?"

        # Aquí podrías agregar requisitos específicos por carrera si los tienes
        return f"Requisitos específicos para {nombre_carrera}:\n\n{requisitos_generales}\n\n(Pueden variar según la carrera, confirma con admisiones)."

    # Preguntas sugeridas para el usuario
    preguntas_sugeridas = """
    ¿Quieres que te muestre los costos de inscripción y matrícula?
    ¿Deseas conocer las fechas de inicio de clases?
    ¿Quieres que te muestre carreras en modalidad online para facilitar tu ingreso?
    ¿Deseas saber si puedes aplicar a becas o descuentos en la matrícula?
    """

    response = f"""
    {requisitos_generales}

    Preguntas sugeridas para continuar:
    {preguntas_sugeridas}
    """

    return response


@tool
async def matricular(nombre_carrera: str) -> str:
    """
    Simula la matriculación de una carrera en la UBE.
    Retorna un mensaje de confirmación y un link de pago.
    """

    if not nombre_carrera:
        return "Por favor, indica el nombre de la carrera que deseas matricular."

    # Aquí podrías agregar validaciones reales usando get_id_by_name si quieres
    # id_carrera = get_id_by_name(await carreras_manager.get_carreras(), nombre_carrera)
    # if not id_carrera:
    #     return f"No encontré la carrera '{nombre_carrera}'. Verifica el nombre."

    # Generar mensaje de confirmación y link de pago de ejemplo
    link_pago = f"https://ube.edu.ec/pago/matricula?carrera={nombre_carrera.replace(' ', '%20')}&token=EJEMPLO123"

    response = f"""
        ¡Matricula realizada exitosamente para la carrera '{nombre_carrera}'! 🎓

        Para completar el proceso, realiza tu pago en el siguiente link:
        {link_pago}

        Recuerda que tu matrícula se confirmará una vez recibido el pago.
    """

    return response


@tool
async def default_tool() -> str:
    """
    Skill por defecto que responde cuando el usuario hace consultas
    fuera del alcance definido (carreras, grupos, mallas, matrículas de la UBE).
    """
    return (
        "No puedo resolver preguntas como operaciones matemáticas u otros temas externos. "
        "¿Quieres que te muestre información sobre nuestras carreras o procesos de matrícula?\n\n"
        "Si deseas más información puedes comunicarte por:\n"
        "- 📲 WhatsApp: https://api.whatsapp.com/send/?phone=593989758382&text=Me+gustar%C3%ADa+saber+informaci%C3%B3n+sobre+las+carreras&type=phone_number&app_absent=0\n"
        "- 🌐 Página oficial: https://ube.edu.ec/"
    )


tools = [listar_carreras, listar_malla, listar_grupos, listar_detalle_carrera, requisitos_matriculacion]

# El prompt del sistema que define el rol del agente
system_prompt_template = """
    Eres "Dr. Matrícula", un agente virtual de la Universidad Bolivariana del Ecuador (UBE).

    FUNCIÓN ESPECÍFICA:
    - Carreras de pregrado (3er nivel) y postgrado (4to nivel) de la Universidad Bolivariana del Ecuador (UBE).
    - Procesos de matrícula y requisitos de admisión.
    - Mallas curriculares detalladas.
    - Grupos y horarios disponibles.

    INSTRUCCIONES:
    1. SOLO respondes consultas relacionadas con la Universidad Bolivariana del Ecuador (UBE)
    2. Sé cordial, profesional y preciso
    3. Si no tienes información, sugiere contactar directamente a la UBE
    4. Utiliza las herramientas disponibles
    5. **INSTRUCCIÓN CRÍTICA:** Cuando las herramienta `listar_malla` o `listar_grupos` retorna información estructurada y detallada, DEBES incluir la información completa y formateada en tu respuesta final, sin resumirla, añadiendo una introducción cordial y las preguntas sugeridas al final.

    TONO: Profesional, amigable y servicial.
    """

# ==================== LLM Y AGENTE ====================


memorias = {}

from copy import deepcopy

def get_agent(chat_id: int):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0].prompt.template = system_prompt_template
    agent = create_openai_functions_agent(llm, tools, prompt)

    if chat_id in memorias:
        memory = deepcopy(memorias[chat_id])
    else:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        memorias[chat_id] = memory

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_iterations=5,
        handle_parsing_errors=True
    )

    return agent_executor



from langchain_core.tools import tool
import logging

from core.utils.memory_manager import memoria_manager

logger = logging.getLogger(__name__)

@tool
async def listar_informacion_general():
    """
    Esta tool se activa cuando el usuario pregunta por informacion general de la UBE comoÑ
    - ¿Qué es la UBE?
    - ¿Cuál es la visión de la universidad?
    - ¿Cuál es ma misión de la universidad?
    - ¿Porqué elegir la UBE?
    """
    return """
    ### ¿Quiénes somos?
    La Universidad Bolivariana del Ecuador (UBE), la Universidad para todos, es una Universidad particular autofinanciada de derecho privado, sin fines de lucro, que forma parte del Sistema de Educación Superior del Ecuador. La UBE fue creada mediante Ley de Creación de Universidades emitida por la Asamblea Nacional de la República del Ecuador el 4 de mayo de 2021 y publicada en el Quinto Suplemento del Registro Oficial 452 del 14 de mayo de 2021.

    ### Nuestra misión
    Formar profesionales y académicos competentes y humanistas, ciudadanos autónomos, a través de la docencia, investigación y vinculación con la sociedad, guiados por principios universales, generar y difundir conocimiento científico y tecnológico, y diálogo de saberes, fortaleciendo la inclusión, equidad y la interculturalidad, aportando en la resolución de problemas personales, colectivos y ambientales, para alcanzar el desarrollo humano del buen vivir.

    ### Nuetra visión
    Ser la universidad humanista, científica-tecnológica y de los saberes, internacionalizada y solidaria, con alta identidad en el ámbito latinoamericano por su responsabilidad social, la democratización cognitiva, formación inter y transdisciplinaria, con compromiso ciudadano, a través de una educación centrada en los sujetos y el desarrollo del contexto.

    ### ¿Por qué elegir UBE?
    - La UBE es la elección favorita de estudiantes en todo el Ecuador por varias razones:
    - Ofrece programas académicos avanzados en una variedad de áreas de estudio y en las modalidades presencial, hibrida y en línea.
    - Se destaca por fusionar áreas del conocimientos y por ofrecer una educación inter y transdisciplinar.
    - Capacita a los estudiantes de grado y postgrado para pensar creativamente y generar descubrimientos inimaginables.
    - Estudia, desde sus dominios académicos, las problematicas sociales con enfoque integral e inclusivo.
    - Se enfoca en democratizar el acceso a la educación superior para contribuir al propósito institucional de ser la universidad para todos.
    """


@tool
async def listar_beneficios():
    """
    Devuelve beneficios que ofrece la UBE.
    Si dice: “¿Qué modalidades de estudio hay?”, muestra solo la sección de “Modalidades de estudio”.
    Si pregunta: “¿Tienen becas o apoyo psicológico?”, responde con la parte correspondiente a “Bienestar y vida estudiantil”.
    Devuelve una descripción detallada de las principales instalaciones y beneficios.
    """

    academicos = """
    ## Beneficios académicos
    - Conectividad Wi-Fi en todo el campus.
    - Laboratorios especializados: de simulación clínica, informática, multimedia, idiomas, robótica, entre otros.
    - Tutorías personalizadas y asesorías académicas.
    - Convenios con instituciones y hospitales para prácticas preprofesionales.
    - Aulas inteligentes equipadas con proyectores, pantallas táctiles y conexión a internet.
    """

    digital = """
    ## 💻 3. Ecosistema digital
    - Plataforma de gestión académica integral (SGA) para calificaciones, tareas, pagos y asistencia.
    - Campus virtual UBE Online, con acceso a clases en vivo, grabaciones y materiales descargables.
    - App institucional para smartphones (consultas, noticias, horarios y servicios).
    - Correo institucional y almacenamiento en la nube para todos los estudiantes.
    - Soporte técnico y acompañamiento digital.
    """

    modalidades = """
    ## 🧑‍🏫 Modalidades de estudio
    - Presencial: clases en el campus, con práctica directa en laboratorios y aulas equipadas.
    - Híbrida: combina clases presenciales con sesiones virtuales en tiempo real.
    - En línea: modalidad 100% virtual con acompañamiento docente, foros y material multimedia.
    - Horarios flexibles para estudiantes que trabajan.
    - Acceso a recursos virtuales 24/7 (aulas virtuales, grabaciones, materiales).
    """

    bienestar = """
    ## Bienestar y vida estudiantil
    - Áreas verdes y zonas de descanso.
    - Servicio de orientación psicológica y consejería estudiantil.
    - Programas de becas y ayudas económicas.
    - Clubes estudiantiles y grupos culturales.
    - Actividades culturales, deportivas y recreativas.
    """

    complementarios = """
    ## 🏢 Servicios del campus
    - Cafeterías, comedores y áreas de descanso.
    - Centro médico universitario (Enfermería).
    - Parqueaderos y transporte institucional.
    - Seguridad y monitoreo 24/7 en todo el campus.
    - Zonas verdes y espacios recreativos.
    """

    profesional = """
    ## 🌎 Proyección y desarrollo profesional
    - Bolsa de empleo y vinculación con empresas.
    - Charlas y ferias laborales.
    - Programas de emprendimiento y capacitación continua.
    """

    sostenibilidad = """
    ## 🌱 Sostenibilidad e inclusión
    - Políticas de sostenibilidad ambiental: reciclaje, ahorro energético y campañas ecológicas.
    - Infraestructura accesible para personas con discapacidad.
    - Programas de inclusión social y equidad de género.
    """

    return f"""
    {academicos}

    {digital}

    {modalidades}

    {bienestar}

    {complementarios}

    {profesional}

    {sostenibilidad}
    """

@tool
async def default_tool() -> str:
    """
    Skill por defecto que responde cuando el usuario hace consultas
    fuera del alcance definido.
    """
    return (
        "No puedo resolver preguntas como operaciones matemáticas u otros temas externos. "
        "¿Quieres que te muestre información sobre nuestras carreras o procesos de matrícula?\n\n"
        "Si deseas más información puedes comunicarte por:\n"
        "- 📲 WhatsApp: https://api.whatsapp.com/send/?phone=593989758382&text=Me+gustar%C3%ADa+saber+informaci%C3%B3n+sobre+las+carreras&type=phone_number&app_absent=0\n"
        "- 🌐 Página oficial: https://ube.edu.ec/"
    )

@tool
async def informacion_becas():
    """
    Retorna información detallada sobre los requisitos y condiciones
    para acceder a becas y ayudas económicas en la Universidad Bolivariana del Ecuador.
    """

    becas = """
    🎓 **BECAS – Requisitos para el otorgamiento**

    Para aplicar a una beca en la Universidad Bolivariana del Ecuador (UBE), el estudiante debe cumplir con los siguientes requisitos:

    - Estar **matriculado** en el período académico correspondiente.
    - No tener **sanciones disciplinarias** emitidas por el Consejo Superior Universitario.
    - No mantener **deudas u obligaciones pendientes** con la institución.
    - No poseer **otros descuentos o becas** activas.
    - Completar la **solicitud oficial** disponible en el Sistema de Gestión Académica (**SGA UBE**).
    """

    ayuda_economica = """
    💰 **AYUDAS ECONÓMICAS – Requisitos para el otorgamiento**

    Las ayudas económicas están destinadas a apoyar a los estudiantes que enfrentan condiciones especiales o de vulnerabilidad. Para acceder a este beneficio se requiere:

    - Tener **dos o más familiares** (hermanos o cónyuges) matriculados en la UBE y que dependan económicamente de la misma persona.  
      *(La ayuda se otorgará solo a uno de los familiares).*
    - Residir en **provincias o cantones alejados de Guayaquil**, y que un **estudio socioeconómico** justifique la necesidad del beneficio.
    - Haber sido **abanderado o portaestandarte** en su institución de educación anterior.
    - Presentar **casos especiales comprobables**, como enfermedades graves, accidentes, fallecimiento de un familiar directo, despidos intempestivos o tener un familiar dependiente con discapacidad.
    - Ser **empleado** o **familiar** de una empresa con **convenio de cooperación interinstitucional** con la UBE.

    📘 *Las ayudas económicas podrán cubrir hasta el 20% del valor de la colegiatura de estudiantes regulares, según los resultados del estudio socioeconómico.*

    ⚠️ **Importante:**  
    - Los estudiantes de **programas de posgrado** o **carreras de carácter especial o de profundización** no pueden acceder a becas o ayudas económicas, ya que estos programas cuentan con descuentos propios.  
    - Se exceptúan los estudiantes con **discapacidad** y los pertenecientes a **convenios interinstitucionales**, quienes sí pueden aplicar a los beneficios.
    """

    return f"""
    La UBE ofrece distintos programas de **becas** y **ayudas económicas** destinados a apoyar el desarrollo académico y social de sus estudiantes.

    {becas}

    {ayuda_economica}
    """

@tool
async def ver_contactos():
    """
    Retorna la información de contacto del Departamento de Admisiones
    de la Universidad Bolivariana del Ecuador (UBE).
    """

    return """
    📞 **Departamento de Admisiones – Universidad Bolivariana del Ecuador**

    Si necesitas información sobre inscripciones, carreras o procesos académicos, puedes comunicarte con nosotros a través de los siguientes canales:

    🕒 **Horario de atención:**  
    Lunes a viernes, de **08:00 a 18:00**.

    ✉️ **Correo electrónico:**  
    [admisiones@ube.edu.ec](mailto:admisiones@ube.edu.ec)

    📱 **Teléfono / WhatsApp:**  
    **098 449 0567**

    💬 ¡Nuestro equipo de Admisiones estará encantado de ayudarte!
    """


@tool
async def obtener_enlace_sga():
    """
    Obtiene el enlace al Sistema de Gestión Académica (SGA) de la Universidad Bolivariana del Ecuador.

    Returns:
        str: Enlace formateado en Markdown al SGA
    """
    sga_url = "https://sga.ube.edu.ec/"
    return f"[Sistema de Gestión Académica (SGA)]({sga_url})"


@tool
async def obtener_enlace_pagina_principal():
    """
    Obtiene el enlace a la página web principal de la Universidad Bolivariana del Ecuador.

    Returns:
        str: Enlace formateado en Markdown a la web institucional
    """
    ube_url = "https://ube.edu.ec/"
    return f"[Universidad Bolivariana del Ecuador]({ube_url})"

tools = [
    listar_informacion_general,
    listar_beneficios,
    informacion_becas,
    default_tool,
    ver_contactos,
    obtener_enlace_sga,
    obtener_enlace_pagina_principal
]

system_prompt_template = """
    Eres un agente asistente virtual de la Universidad Bolivariana del Ecuador (UBE).

    FUNCIÓN ESPECÍFICA:

    INSTRUCCIONES:
    1. SOLO respondes consultas relacionadas con la Universidad Bolivariana del Ecuador (UBE)
    2. Sé cordial, profesional y preciso

    TONO: Profesional, amigable y servicial.
    """

def get_public_agent(chat_id: int):
    """Crea agente con memoria persistente por chat_id"""
    from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
    from langchain_classic import hub
    from langchain_google_genai import ChatGoogleGenerativeAI
    from assistant.settings import GEMINI_API_KEY
    from core.utils.gemini_client import get_gemini_client_args

    # LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        client_args=get_gemini_client_args(),
    )

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
from typing import List

from langchain_core.tools import tool
from core.services.ventas_service import fetch_grupos, fetch_malla, fetch_detalle_carrera
from core.utils.carreras_manager import CarrerasManager
from core.utils.memory_manager import memoria_manager
from core.utils.ventas_utils import formatear_texto_carreras, get_id_by_name, mostrar_progreso, matriculas_en_proceso, \
    validar_campos_completos, limpiar_matricula
from schemas.ventas.carreras import CarrerasModel, DetalleCarreraModel, DatosMatriculaModel
import logging


logger = logging.getLogger(__name__)
carreras_manager = CarrerasManager()

@tool
async def listar_carreras(tipo_carrera: str = None) -> str:
    """
    Retorna un resumen completo o filtrado de las carreras de la Universidad Bolivariana del Ecuador (UBE).
    El filtro puede ser por nivel (grado, postgrado o maestría) o por área de interés (salud, tecnología, educación, negocios, etc.).

    Ejemplo de uso:
    - "Deseo información de las carreras"
    - "Quiero información de las carreras de grado"
    - "Qué maestrias ofrecen"
    """

    if not tipo_carrera:
        return """
        ## ¿Qué tipo de programas deseas consultar?
        Puedes pedirme información de cualquiera de estas categorías:
    
        - **Grado**  
          Programas universitarios de tercer nivel.
    
        - **Maestrías**  
          Programas de cuarto nivel de especialización profesional o investigativa.
    
        - **Programas Especiales**  
          Programas de formación académica adicional, diplomados, experticias, cursos avanzados estructurados.
    
        - **Programas de Validación por Ejercicio Profesional**  
          Procesos para obtención de título mediante acreditación de experiencia profesional demostrable.
        """

    carreras: List[CarrerasModel] = await carreras_manager.get_carreras()
    texto = formatear_texto_carreras(carreras, tipo_carrera)

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
    {texto}
    
    Preguntas sugeridas para continuar:
    {preguntas_sugeridas}
    """

# @tool(return_direct=True)
@tool
async def detalle_carrera(nombre_carrera: str) -> str:
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
    carreras: List[CarrerasModel] = await carreras_manager.get_carreras()
    id_carrera = get_id_by_name(carreras, nombre_carrera)
    detalle: DetalleCarreraModel = await fetch_detalle_carrera(id_carrera)

    lineas = [
        f"🎓 **Carrera:** {detalle.general.nombre}",
        f"📜 **Título de graduado:** {detalle.general.titulo}",
        f"📜 **Campo laboral:** {detalle.general.campo_llaboral}"
    ]

    if detalle.general.numero_periodos:
        lineas.append(f"Duración: {detalle.general.numero_periodos} periodos")

    if detalle.modalidades:
        lineas.append(f"🎯 **Modalidades disponibles:** {', '.join(detalle.modalidades)}")
    if detalle.precios:
        precios = detalle.precios
        precios_texto = []
        if precios.inscripcion:
            precios_texto.append(f"- Inscripción: ${precios.inscripcion:,.2f}")
        if precios.matricula:
            precios_texto.append(f"- Matrícula: ${precios.matricula:,.2f}")
        if precios.matricula:
            precios_texto.append(f"-Valor de cuota: ${precios.cuota:,.2f}")
        if precios.num_cuota:
            precios_texto.append(f"- Número de cuotas: {precios.num_cuota} por periodo")
        if precios.pre is not None:
            precios_texto.append(f"- Preuniversitario: ${precios.pre:,.2f}")
        if precios_texto:
            lineas.append("**💰 Precios:**\n" + "\n".join(precios_texto))
    if detalle.descuentos:
        pass

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
    carreras: List[CarrerasModel] = await carreras_manager.get_carreras()
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
        f"""
        ## Grupo {grupo.nombre}
        - **Fecha de inicio de clases aproximado:** {grupo.fecha_inicio}
        - **Sesion:** {grupo.sesion}
        - **Modalidad:** {grupo.modalidad}
        ---
        """
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

    # carreras = await carreras_manager.get_carreras()
    #
    # todas_carreras = []
    # todas_carreras.extend(carreras.grado)
    # todas_carreras.extend(carreras.postgrado)
    #
    # if nombre_carrera:
    #     id_carrera = get_id_by_name(carreras.data, nombre_carrera)
    #     if not id_carrera:
    #         return f"No encontré la carrera '{nombre_carrera}'. ¿Quieres que te muestre los requisitos generales?"
    #
    #     return f"Requisitos específicos para {nombre_carrera}:\n\n{requisitos_generales}\n\n(Pueden variar según la carrera, confirma con admisiones)."

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
async def matricular(
        user_id: str,
        mensaje_usuario: str,
        nombre_carrera: str = None,
        grupo: str = None,
        nombres: str = None,
        apellido_paterno: str = None,
        apellido_materno: str = None,
        correo: str = None,
        numero_celular: str = None,
        tipo_sangre: str = None,
        nacionalidad: str = None,
        raza: str = None,
) -> str:
    """
    Gestiona la matriculación de forma conversacional.

    El LLM debe extraer los datos del mensaje_usuario y pasarlos como parámetros.
    Muestra el progreso en cada interacción.

    Args:
        user_id: Identificador único del usuario
        mensaje_usuario: El mensaje completo del usuario (para contexto)
        [resto]: Datos extraídos del mensaje por el LLM
    """

    # Inicializar datos del usuario si no existen
    if user_id not in matriculas_en_proceso:
        matriculas_en_proceso[user_id] = {}

    datos_actuales = matriculas_en_proceso[user_id]

    # Actualizar con datos proporcionados en este mensaje
    campos = {
        "nombre_carrera": nombre_carrera,
        "grupo": grupo,
        "nombres": nombres,
        "apellido_paterno": apellido_paterno,
        "apellido_materno": apellido_materno,
        "correo": correo,
        "numero_celular": numero_celular,
        "tipo_sangre": tipo_sangre,
        "nacionalidad": nacionalidad,
        "raza": raza,
    }

    # Solo actualizar campos que tengan valor
    datos_nuevos = False
    campos_actualizados = []

    for campo, valor in campos.items():
        if valor and valor != datos_actuales.get(campo):
            datos_actuales[campo] = valor
            datos_nuevos = True
            # Nombres más amigables para mostrar
            nombres_amigables = {
                "nombre_carrera": "carrera",
                "grupo": "grupo",
                "nombres": "nombre",
                "apellido_paterno": "apellido paterno",
                "apellido_materno": "apellido materno",
                "correo": "correo",
                "numero_celular": "celular",
                "tipo_sangre": "tipo de sangre",
                "nacionalidad": "nacionalidad",
                "raza": "raza",
            }
            campos_actualizados.append(nombres_amigables.get(campo, campo))

    # Verificar si faltan campos usando la utilidad
    completos, faltantes = validar_campos_completos(datos_actuales)

    if not completos:
        response = ""

        # Si se agregaron datos nuevos, confirmar específicamente qué se guardó
        if datos_nuevos:
            if len(campos_actualizados) == 1:
                response += f"✅ **Perfecto!** He registrado tu **{campos_actualizados[0]}**.\n\n"
            else:
                campos_str = ", ".join(campos_actualizados[:-1]) + f" y {campos_actualizados[-1]}"
                response += f"✅ **Perfecto!** He registrado: **{campos_str}**.\n\n"

        # Mostrar estado actual
        response += mostrar_progreso(datos_actuales)

        # Sugerencia contextual de qué datos proporcionar
        if not datos_actuales.get("nombre_carrera"):
            response += "\n\n💡 **Tip:** Puedes decirme algo como *\"Quiero matricularme en Derecho\"*"
        elif not datos_actuales.get("grupo"):
            response += "\n\n💡 **Tip:** Dime en qué grupo te gustaría estar *(A, B, C, etc.)*"
        elif not datos_actuales.get("nombres") or not datos_actuales.get("apellido_paterno"):
            response += "\n\n💡 **Tip:** Dime tu nombre completo, por ejemplo: *\"Me llamo Juan Pérez\"*"
        elif not datos_actuales.get("correo"):
            response += "\n\n💡 **Tip:** Necesito tu correo electrónico, ejemplo: *juan@email.com*"
        elif not datos_actuales.get("numero_celular"):
            response += "\n\n💡 **Tip:** Por último, tu número de celular en formato: *+593987654321*"

        return response

    # Validar formato de datos antes de procesar
    try:
        datos_validados = DatosMatriculaModel(**datos_actuales)
    except Exception as e:
        error_msg = str(e)
        if "numero_celular" in error_msg:
            # Limpiar el celular de datos_actuales para que vuelva a aparecer como faltante
            datos_actuales.pop("numero_celular", None)
            return f"❌ **Error:** El número de celular debe tener el formato **+593XXXXXXXXX**\n\nEjemplo: +593987654321\n\n{mostrar_progreso(datos_actuales)}"
        elif "correo" in error_msg:
            datos_actuales.pop("correo", None)
            return f"❌ **Error:** El correo electrónico no es válido.\n\nPor favor ingresa un correo válido como: ejemplo@email.com\n\n{mostrar_progreso(datos_actuales)}"
        else:
            return f"❌ **Error en los datos:** {error_msg}\n\n{mostrar_progreso(datos_actuales)}"

    # ✅ TODOS LOS DATOS COMPLETOS - Procesar matrícula
    link_pago = f"https://ube.edu.ec/pago/matricula?carrera={datos_actuales['nombre_carrera'].replace(' ', '%20')}&token={user_id[:8].upper()}"

    response = """
🎉 **¡MATRÍCULA REALIZADA EXITOSAMENTE!** 🎓

**━━━━━━━━━━━━━━━━━━━━━━━━━━━**

**📋 Resumen de tu matrícula:**
"""

    response += f"""
📚 **Carrera:** {datos_actuales['nombre_carrera']}
👥 **Grupo:** {datos_actuales['grupo']}
👤 **Estudiante:** {datos_actuales['nombres']} {datos_actuales['apellido_paterno']}"""

    if datos_actuales.get('apellido_materno'):
        response += f" {datos_actuales['apellido_materno']}"

    response += f"""
📧 **Correo:** {datos_actuales['correo']}
📱 **Celular:** {datos_actuales['numero_celular']}
"""

    if datos_actuales.get('nacionalidad'):
        response += f"🌍 **Nacionalidad:** {datos_actuales['nacionalidad']}\n"
    if datos_actuales.get('tipo_sangre'):
        response += f"🩸 **Tipo de Sangre:** {datos_actuales['tipo_sangre']}\n"

    response += f"""
**━━━━━━━━━━━━━━━━━━━━━━━━━━━**

💳 **Completa tu pago aquí:**
🔗 {link_pago}

⏰ **Importante:** Tu matrícula se confirmará una vez recibido el pago.

📧 Te hemos enviado los detalles a tu correo: {datos_actuales['correo']}

✨ ¿Necesitas ayuda con algo más?
"""

    # await enviar_a_matricular(datos_actuales)
    limpiar_matricula(user_id)
    print(f"POSIII: {datos_actuales}")
    return response.strip()


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


tools = [
    listar_carreras,
    detalle_carrera,
    listar_malla,
    listar_grupos,
    requisitos_matriculacion,
    default_tool,
    matricular
]

# El prompt del sistema que define el rol del agente
system_prompt_template = """
    Eres un agente vendedor virtual de carreras de la Universidad Bolivariana del Ecuador (UBE).

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

    TONO: Profesional, amigable y servicial.
    """

# ==================== LLM Y AGENTE ====================


def get_ventas_agent(chat_id: int):
    """Crea agente con memoria persistente por chat_id"""
    from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
    from langchain_classic import hub
    from langchain_google_genai import ChatGoogleGenerativeAI
    from assistant.settings import GEMINI_API_KEY
    from core.utils.gemini_client import get_gemini_client_args

    # ✅ Validaciones
    if not isinstance(chat_id, int) or chat_id <= 0:
        raise ValueError(f"chat_id inválido: {chat_id}")

    logger.info(f"📊 Creando agente para chat_id: {chat_id}")

    # LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        client_args=get_gemini_client_args(),
    )

    # Prompt
    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0].prompt.template = system_prompt_template

    # Agent
    agent = create_openai_functions_agent(llm, tools, prompt)

    # ✅ CRÍTICO: Obtener memoria del manager (reutilizar si existe)
    memory = memoria_manager.get_memory(chat_id)

    # Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_iterations=5,
        handle_parsing_errors=True
    )

    logger.info(f"✅ Agente listo | Memorias activas: {memoria_manager.get_size()}")
    return agent_executor
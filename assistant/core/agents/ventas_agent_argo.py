# core/ai/argo_agent.py
import argo
from argo.skills import chat
from assistant.settings import GEMINI_API_KEY
from core.services.ventas_service import fetch_carreras, fetch_grupos, fetch_malla

from core.utils.ventas_utils import formatear_texto_carreras, get_id_by_name
from schemas.ventas.carreras import CarrerasModel


def initialize_agent():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    llm = argo.LLM(
        model="gemini-2.0-flash",
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        verbose=True,
    )

    agent = argo.ChatAgent(
        name="Dr. Matrícula",
        description="Asistente que brinda información de carreras de la UBE.",
        llm=llm,
        skills=[chat],
    )

    agent.system_prompt = """
    Eres Dr. Matrícula, un asistente especializado en información académica de la UBE.

    IMPORTANTE: Cuando el usuario mencione el NOMBRE de una carrera específica (como "derecho", "psicología", "enfermería"), 
    siempre usa skill_listar_carreras para mostrar la información completa de esa carrera.

    INSTRUCCIONES:
    - Para preguntas sobre carreras específicas o información general de carreras → skill_listar_carreras
    - Para preguntas sobre grupos, paralelos o fechas de inicio → skill_listar_grupos  
    - Para preguntas sobre malla curricular → skill_listar_malla
    - Para matricularse → skill_matricular
    - Para otros temas → skill_default

    EJEMPLOS:
    - "dame información de derecho" → skill_listar_carreras
    - "qué carreras tienen" → skill_listar_carreras
    - "grupos de psicología" → skill_listar_grupos
    - "malla de enfermería" → skill_listar_malla
    """

    carreras_instance: CarrerasModel = fetch_carreras()
    agent.carreras: CarrerasModel  = carreras_instance

    @agent.tool
    async def list_carreras():
        """
        Retorna un resumen completo de las carreras de la UBE.
        Retorna información de carreras específicas según se solicita.
        Los IDS se usan solo para apuntar a otro endpoint de ser necesario,
        no se muestran en la conversación con el usuario.

        Incluye:
        - Nombre de la carrera.
        - Precios de inscripción, matrícula y número de cuotas.
        - Sesiones.
        - Modalidades.
        """
        grado = formatear_texto_carreras(agent.carreras.grado, "grado")
        postgrado = formatear_texto_carreras(agent.carreras.postgrado, "postgrado")

        preguntas_sugeridas = [
            "¿Prefieres que te muestre únicamente las carreras de pregrado o las de postgrado?",
            "¿Quieres conocer los requisitos de ingreso para una carrera en particular?",
            "¿Te interesa saber la duración promedio de una carrera o una maestría?",
            "¿Quieres ver cuáles carreras están disponibles en modalidad online, presencial o híbrida?",
            "¿Prefieres que te organice las carreras por áreas como salud, tecnología, educación o negocios?",
            "¿Quieres información sobre becas, descuentos o facilidades de pago?",
            "¿Te interesa conocer las oportunidades laborales de una carrera específica?",
            "¿Deseas que te muestre los grupos y fechas de inicio más cercanos?",
            "¿Quieres que te sugiera carreras relacionadas a tus intereses?",
            "¿Te gustaría comparar dos carreras para ver cuál se ajusta mejor a lo que buscas?"
        ]

        response = (
                f"{grado}\n\n"
                f"{postgrado}\n\n"
                f"Preguntas sugeridas para continuar:\n" + "\n".join(preguntas_sugeridas)
        )
        return response

    @agent.tool
    async def listar_grupos(nombre_carrera: str):
        """
        Lista los grupos de una carrera específica a partir de su nombre.
        Si la carrera no existe o no tiene grupos próximos, retorna un mensaje adecuado.
        """
        id_carrera = get_id_by_name(agent.carreras, nombre_carrera)

        if not id_carrera:
            return f"No se encontró la carrera '{nombre_carrera}'."

        grupos = fetch_grupos(id_carrera)

        if not grupos:
            return f"No hay grupos disponibles para la carrera '{nombre_carrera}' que inicien próximamente."

        response = [f"Grupos disponibles para la carrera '{nombre_carrera}':"]
        for grupo in grupos:
            response.append(
                f"- Paralelo {grupo.nombre} | Inicio: {grupo.fecha_inicio} | Sesión: {grupo.sesion} | Modalidad: {grupo.modalidad}"
            )

        return "\n".join(response)

    @agent.tool
    async def listar_malla(nombre_carrera: str):
        """
        Lista la malla de una carrera específica a partir de su nombre.
        Si la carrera no existe, retorna un mensaje adecuado.
        """
        id_carrera = get_id_by_name(agent.carreras, nombre_carrera)
        malla_instance = fetch_malla(id_carrera)
        malla = malla_instance.data if malla_instance else None

        if not malla:
            response = "No hay malla disponible para esta carrera."
        else:
            response = f"La Malla curricular de la carrera es la siguiente:\n"

            for nivel in malla:
                response += f"\n### Período: {nivel.nivel_malla}"
                response += f"\nLas asignaturas de este período son:"

                for asig in nivel.asignaturas:
                    response += f"\n- Asignatura: {asig.asignatura}"
                    response += f"\n  - Horas: {asig.horas}"
                    if asig.creditos is not None:
                        response += f"\n  - Créditos: {asig.creditos}"
            response += "\n"
        return response

    @agent.skill
    async def skill_listar_carreras(ctx: argo.Context):
        """
        Skill principal para mostrar información de carreras específicas o generales.
        Se activa cuando el usuario menciona nombres de carreras o pide información académica.
        Ejemplos: "información de derecho", "qué carreras hay", "precios de psicología"
        """
        tool = await ctx.equip(tools=[list_carreras])
        result = await ctx.invoke(tool)
        ctx.add(argo.Message.system(result))
        await ctx.reply()

    @agent.skill
    async def skill_listar_grupos(ctx: argo.Context):
        """
        Skill para grupos, paralelos y fechas de inicio de carreras específicas.
        Se activa con palabras como: "grupos", "paralelos", "cupos", "fechas", "cuándo inicia"
        """
        tool = await ctx.equip(tools=[listar_grupos])
        result = await ctx.invoke(tool)  # Aquí se obtiene el resultado real (string)
        ctx.add(argo.Message.system(result))  # Lo agregas a la conversación
        await ctx.reply()  # Esto manda la respuesta al frontend

    @agent.skill
    async def skill_listar_malla(ctx: argo.Context):
        """
        Skill para malla curricular y plan de estudios.
        Se activa con palabras como: "malla", "plan de estudios", "asignaturas", "materias"
        """
        tool = await ctx.equip(tools=[listar_malla])
        result = await ctx.invoke(tool)
        ctx.add(argo.Message.system(result))
        await ctx.reply()

    @agent.skill
    async def skill_matricular(ctx: argo.Context):
        """
        Skill para procesos de matrícula e inscripción.
        Se activa con palabras como: "matricular", "inscribir", "estudiar"
        """
        result = f"¡Excelente! Tu matrícula ha sido creada con éxito. Un gran paso hacia tu futuro profesional.\n\nPara completar el proceso, contacta al número 09998989. Él te guiará en los siguientes pasos."
        ctx.add(argo.Message.system(result))
        await ctx.reply()

    @agent.skill
    async def skill_default(ctx: argo.Context):
        """
        Skill por defecto para consultas fuera del ámbito académico.
        Se activa cuando ninguna otra skill es apropiada.
        """
        mensaje_fuera_de_contexto = (
            "Solo puedo ayudarte con información sobre carreras y matrículas de la UBE. "
            "¿Te interesa conocer alguna de nuestras carreras?"
        )
        ctx.add(argo.Message.system(mensaje_fuera_de_contexto))
        await ctx.reply()

    return agent

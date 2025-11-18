from typing import List

from openai import OpenAI
import json

from assistant.settings import GEMINI_API_KEY
from schemas.ventas.carreras import CarrerasModel


def get_id_by_name(carreras: List[CarrerasModel], mensaje: str):
    """
    Extrae el nombre de la carrera de un mensaje y devuelve su ID.
    El modelo de IA actúa como un clasificador.
    """

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
    )

    prompts = {}
    for tipo_carrera in carreras:
        for area in tipo_carrera.areas:
            for carrera in area.carreras:
                prompts[carrera.id] = carrera.nombre

    classifier_prompt = """
    Eres un clasificador de carreras universitarias.
    Tu tarea es extraer el nombre de la carrera del mensaje del usuario y encontrar la coincidencia más cercana en la siguiente lista.
    Si encuentras una coincidencia, responde únicamente con el ID correspondiente en formato JSON.
    Si no hay una coincidencia clara, o si el mensaje no contiene una carrera, responde con el ID 0.
    Lista de carreras:
    {prompts_str}

    Responde ÚNICAMENTE en formato JSON, con la llave "id". Ejemplo de respuesta:
    {{"id": 123}}
    """

    prompts_str = json.dumps(prompts, indent=2, ensure_ascii=False)

    messages = [
        {"role": "system", "content": classifier_prompt.format(prompts_str=prompts_str)},
        {"role": "user", "content": f"Mensaje a clasificar: {mensaje}"}
    ]

    try:
        classification = client.chat.completions.create(
            # model="meta-llama/llama-3.3-70b-instruct",
            model="gemini-2.0-flash",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )

        response_json = json.loads(classification.choices[0].message.content)
        category_id = int(response_json.get("id", None))

        return category_id

    except Exception as e:
        print(f"Error al procesar la respuesta del modelo: {e}")
        return None

def formatear_texto_carreras(
    data: list,
    tipo_carrera: str | None = None
) -> str:
    """
    Recibe el JSON de carreras (lista de CarrerasModel / TipoCarreraModel) y devuelve un texto formateado.
    """

    if tipo_carrera:
        data = [item for item in data if item.tipo.lower() == tipo_carrera.lower()]

    # Agrupar por tipo y luego por área
    tipos_dict = {}

    for item in data:
        tipo_nombre = item.tipo

        for area_item in item.areas:
            if tipo_nombre not in tipos_dict:
                tipos_dict[tipo_nombre] = {}

            if area_item.nombre not in tipos_dict[tipo_nombre]:
                tipos_dict[tipo_nombre][area_item.nombre] = []

            for carrera in area_item.carreras:
                tipos_dict[tipo_nombre][area_item.nombre].append(carrera.nombre)

    if not tipos_dict:
        return "No se encontraron carreras con el filtro solicitado."

    # Formatear la salida
    lines = []
    for tipo_nombre, areas in tipos_dict.items():
        lines.append(f"## {tipo_nombre}")

        for area_nombre, carreras in areas.items():
            lines.append(f"**{area_nombre}**")
            for carrera in carreras:
                lines.append(f"- {carrera}")

        lines.append("---")

    return "\n".join(lines)


matriculas_en_proceso = {}


def mostrar_progreso(datos: dict) -> str:
    """
    Genera un resumen visual de los datos capturados en el proceso de matrícula.

    Args:
        datos: Diccionario con los datos del usuario capturados hasta el momento

    Returns:
        str: Mensaje formateado con el estado actual de la matrícula
    """

    campos_requeridos = {
        "nombre_carrera": "📚 Carrera",
        "grupo": "👥 Grupo",
        "nombres": "👤 Nombres",
        "apellido_paterno": "👤 Apellido Paterno",
        "correo": "📧 Correo",
        "numero_celular": "📱 Celular",
    }

    campos_opcionales = {
        "apellido_materno": "👤 Apellido Materno",
        "tipo_sangre": "🩸 Tipo de Sangre",
        "nacionalidad": "🌍 Nacionalidad",
        "raza": "📋 Raza",
    }

    # Recopilar datos completos
    completos = []
    for campo, emoji_nombre in campos_requeridos.items():
        if campo in datos and datos[campo]:
            completos.append(f"✅ {emoji_nombre}: **{datos[campo]}**")

    for campo, emoji_nombre in campos_opcionales.items():
        if campo in datos and datos[campo]:
            completos.append(f"✅ {emoji_nombre}: **{datos[campo]}**")

    # Recopilar datos faltantes (solo requeridos)
    faltantes = []
    for campo, emoji_nombre in campos_requeridos.items():
        if campo not in datos or not datos[campo]:
            faltantes.append(f"⏳ {emoji_nombre}")

    # Construir mensaje
    mensaje = "\n**📊 ESTADO DE TU MATRÍCULA**\n\n"

    if completos:
        mensaje += "**Datos registrados:**\n"
        mensaje += "\n".join(completos)
        mensaje += "\n\n"

    if faltantes:
        mensaje += "**Datos pendientes:**\n"
        mensaje += "\n".join(faltantes)
        mensaje += "\n\n"
        mensaje += "💬 Por favor, proporcióname la información que falta."

    # Barra de progreso
    total_requeridos = len(campos_requeridos)
    completados = sum(1 for k in campos_requeridos.keys() if k in datos and datos[k])
    porcentaje = (completados / total_requeridos) * 100 if total_requeridos > 0 else 0

    barra_llena = "█" * int(porcentaje / 10)
    barra_vacia = "░" * (10 - int(porcentaje / 10))

    mensaje += f"\n**Progreso:** {barra_llena}{barra_vacia} {int(porcentaje)}% ({completados}/{total_requeridos})"

    return mensaje


def obtener_campos_faltantes(datos: dict) -> list:
    """
    Retorna una lista de los campos requeridos que faltan.

    Args:
        datos: Diccionario con los datos actuales

    Returns:
        list: Lista de nombres de campos faltantes
    """
    campos_requeridos = ["nombre_carrera", "grupo", "nombres", "apellido_paterno", "correo", "numero_celular"]
    return [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]


def validar_campos_completos(datos: dict) -> tuple[bool, list]:
    """
    Valida si todos los campos requeridos están completos.

    Args:
        datos: Diccionario con los datos actuales

    Returns:
        tuple: (bool: están completos, list: campos faltantes)
    """
    faltantes = obtener_campos_faltantes(datos)
    return len(faltantes) == 0, faltantes


def limpiar_matricula(user_id: str) -> bool:
    """
    Limpia los datos de matrícula de un usuario.

    Args:
        user_id: ID del usuario

    Returns:
        bool: True si se limpió, False si no existía
    """
    if user_id in matriculas_en_proceso:
        del matriculas_en_proceso[user_id]
        return True
    return False
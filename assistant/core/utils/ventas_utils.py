from openai import OpenAI
import json

from assistant.settings import GEMINI_API_KEY
from schemas.ventas.carreras import CarreraBaseModel


def get_id_by_name(carreras, mensaje: str):
    """
    Extrae el nombre de la carrera de un mensaje y devuelve su ID.
    El modelo de IA actúa como un clasificador.
    """

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
    )

    prompts = {}
    if hasattr(carreras, 'grado'):
        for x in carreras.grado:
            prompts[x.id] = x.nombre
    if hasattr(carreras, 'postgrado'):
        for x in carreras.postgrado:
            prompts[x.id] = x.nombre

    classifier_prompt = """
    Eres un clasificador de carreras.
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


def formatear_texto_carreras(carreras: list[CarreraBaseModel], tipo: str):
    """
    Formatea la lista de carreras en texto legible
    """
    msg = ""
    for carrera in carreras:
        msg += f"\n - {carrera.nombre.title()}"

    return f"""
    Las carreras de {tipo} son:
    {msg}
    """
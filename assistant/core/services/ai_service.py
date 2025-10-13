from argo.client import stream
from asgiref.sync import sync_to_async
from core.agents.ventas_agent import initialize_agent
from core.models import ChatHistory

agent = initialize_agent()


async def get_ai_response(user_message: str, chat_id: int = None) -> str:
    """
    Envía un mensaje al agente Argo con contexto del chat y devuelve la respuesta generada por la IA.

    Args:
        user_message: Mensaje del usuario
        chat_id: ID del chat para mantener contexto
    """
    try:
        # Obtener historial del chat si existe
        if chat_id:
            chat_history = await sync_to_async(list)(
                ChatHistory.objects.filter(chat_id=chat_id).order_by('created_at')
            )
            messages = []
            for history_item in chat_history:
                if history_item.from_ai:
                    messages.append(f"Asistente: {history_item.message}")
                else:
                    if history_item.message != user_message:
                        messages.append(f"Usuario: {history_item.message}")

            # Construir mensaje completo con contexto
            if messages:
                context_str = "\n".join(messages)
                full_message = f"Historial de conversación:\n{context_str}\n\nNuevo mensaje del usuario: {user_message}"
            else:
                full_message = user_message
        else:
            full_message = user_message

        # El nuevo agente maneja mejor las respuestas, filtro más simple
        response_generator = stream(agent, full_message)

        # Capturar toda la respuesta
        full_response = ""
        for chunk in response_generator:
            if chunk:
                full_response += str(chunk)

        # Filtro simple: remover solo metadatos obvios del agente
        lines = full_response.split('\n')
        cleaned_lines = []

        for line in lines:
            # Mantener líneas que no sean metadatos del framework
            if (line.strip() and
                    not line.startswith("Choose(") and
                    not line.strip() in ["```", "```json"]):
                cleaned_lines.append(line)

        response = '\n'.join(cleaned_lines).strip()
        response = response if response else "No se recibió respuesta del agente."

        return response if response and response.strip() else "No se recibió respuesta del agente."

    except Exception as e:
        print(f"Error in get_ai_response: {e}")
        import traceback
        traceback.print_exc()
        return f"Lo siento, ocurrió un error: {str(e)}"
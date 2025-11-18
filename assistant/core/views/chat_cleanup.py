from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView as DRFAPIView
from core.agents.ventas_agent import memoria_manager
from core.authentication.backend_auth import BackendTokenAuthentication
from core.models import Chat
import logging


logger = logging.getLogger(__name__)

class ChatCleanupView(DRFAPIView):
    """Limpia la memoria de un chat específico"""

    authentication_classes = [BackendTokenAuthentication]
    permission_classes = [IsAuthenticated]

    async def delete(self, request, chat_id):
        """DELETE /chat/{chat_id}/cleanup"""

        try:
            # ✅ Validar chat_id
            if not isinstance(chat_id, int) or chat_id <= 0:
                return Response(
                    {"detail": "chat_id inválido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = request.user

            # ✅ Verificar que el chat pertenece al usuario
            try:
                chat = await sync_to_async(Chat.objects.get)(
                    id=chat_id,
                    user_id=str(user.id)
                )
            except Chat.DoesNotExist:
                logger.warning(f"❌ Intento de acceso no autorizado a chat {chat_id}")
                return Response(
                    {"detail": "Chat no encontrado o no pertenece a tu cuenta"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # ✅ Limpiar memoria
            memoria_manager.clear_memory(chat_id)
            logger.info(f"🗑️ Memoria limpiada para chat: {chat_id}")

            return Response(
                {
                    "message": f"Memoria del chat {chat_id} eliminada",
                    "chats_activos": memoria_manager.get_size()
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"❌ Error en ChatCleanupView: {e}", exc_info=True)
            return Response(
                {"detail": "Error procesando solicitud"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
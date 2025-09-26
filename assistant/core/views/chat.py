from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.authentication.backend_auth import BackendTokenAuthentication
from core.models import Chat, ChatHistory, Provider
from datetime import datetime
import asyncio
from core.services.ventas_service import get_ai_response

class ChatView(APIView):
    authentication_classes = [BackendTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print(user)

        message = request.data.get("message")
        provider, _ = Provider.objects.get_or_create(name=request.data.get("provider"))

        chat_id = request.data.get("chat_id")

        if chat_id:
            chat = Chat.objects.get(id=chat_id)
        else:
            chat = Chat.objects.create(
                user_id=str(user.id),  # tu SimpleUser.id
                provider=provider,
                created_at=datetime.now()
            )

        ChatHistory.objects.create(
            chat=chat,
            message=message,
            created_at=datetime.now(),
            from_ai=False
        )

        ai_response = asyncio.run(get_ai_response(message))

        # Guardar respuesta de la IA
        ChatHistory.objects.create(chat=chat, text=ai_response, from_ai=True)

        return Response({
            "chat_id": chat.id,
            "user_message": message,
            "ai_response": ai_response,
        })

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.agents.classifier import route_message
from core.models import Chat, ChatHistory, Provider
from core.authentication.backend_auth import BackendTokenAuthentication
from datetime import datetime
from asgiref.sync import sync_to_async
from core.utils.memory_manager import memoria_manager


class ChatView(APIView):
    authentication_classes = [BackendTokenAuthentication]
    permission_classes = [IsAuthenticated]

    async def post(self, request):
        """Procesa un mensaje manteniendo contexto de conversación"""
        data = request.data
        user = request.user
        message = data.get("message")

        provider = await sync_to_async(Provider.objects.get)(name=data.get("provider"))
        chat_id = data.get("chat_id")

        print(provider.id)
        print(data)

        if chat_id:
            chat = await sync_to_async(Chat.objects.get)(id=chat_id)
        else:
            chat = await sync_to_async(Chat.objects.create)(
                user_id=str(user.id),
                provider=provider,
                created_at=datetime.now()
            )

        await sync_to_async(ChatHistory.objects.create)(
            chat=chat,
            message=message,
            created_at=datetime.now(),
            from_ai=False
        )

        # agent_executor = get_router_agent(chat.id)

        # category, ai_response = await route_message(chat_id, message, request.auth, provider)
        category, ai_response = await route_message(
            chat_id=chat.id,
            user_message=message,
            token=request.auth,
            provider=provider
        )
        # agent_executor = get_agent(chat.id)
        # result = await agent_executor.ainvoke({"input": message})
        # ai_response = result.get("output", "Ocurrió un error inesperado.")

        await sync_to_async(ChatHistory.objects.create)(
            chat=chat,
            message=ai_response,
            created_at=datetime.now(),
            from_ai=True
        )

        # return Response({
        #     "chat_id": chat.id,
        #     "respuesta": ai_response
        # })

        return Response({
            "chat_id": chat.id,
            "category": category,
            "respuesta": ai_response,
            "contexto_activo": memoria_manager.get_size()
        })
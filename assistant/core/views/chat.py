from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.agents.ventas_agent2 import get_agent
from core.models import Chat, ChatHistory, Provider
from core.authentication.backend_auth import BackendTokenAuthentication
from datetime import datetime
from asgiref.sync import sync_to_async
from core.agents.router_agent import get_router_agent

class ChatView(APIView):
    authentication_classes = [BackendTokenAuthentication]
    permission_classes = [IsAuthenticated]

    async def post(self, request):
        print(f"USUARIO QUE ESCRIBE: {request.user}")
        print(request.data)

        data = request.data
        user = request.user
        message = data.get("message")

        provider = await sync_to_async(Provider.objects.get)(name=data.get("provider"))
        chat_id = data.get("chat_id")

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

        # agent_executor = get_agent(chat.id)
        agent_executor = get_router_agent(chat.id)
        result = await agent_executor.ainvoke({"input": message})
        ai_response = result.get("output", "Ocurrió un error inesperado.")

        await sync_to_async(ChatHistory.objects.create)(
            chat=chat,
            message=ai_response,
            created_at=datetime.now(),
            from_ai=True
        )

        return Response({
            "chat_id": chat.id,
            "respuesta": ai_response
        })

from adrf.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.authentication.backend_auth import BackendTokenAuthentication
from core.models import Chat
from rest_framework.response import Response


class ChatHistoryView(APIView):
    authentication_classes = [BackendTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chats = Chat.objects.filter(user_id=user.id).order_by('-id')

        response = [
            {
                'id': x.id,
                'title': x.title
            } for x in chats
        ]
        return Response(response)
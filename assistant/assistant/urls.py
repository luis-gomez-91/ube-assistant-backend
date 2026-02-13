from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views.chat_cleanup import ChatCleanupView
from core.views.chat_history import ChatHistoryView
from core.views.profile import ProfileView
from core.views.chat import ChatView
from core.views import HomeView

schema_view = get_schema_view(
    openapi.Info(
        title="UBE Assistant API",
        default_version="v1",
        description="API del backend UBE Assistant: autenticación, chat con IA, perfil y gestión de conversaciones.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls, name="admin"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("chat/", ChatView.as_view(), name="chatbot"),
    path("chat/history/", ChatHistoryView.as_view(), name="chats-history"),
    path("chat/<int:chat_id>/cleanup/", ChatCleanupView.as_view(), name="chat-cleanup"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

from django.contrib import admin
from django.urls import path

from core.views.chat_cleanup import ChatCleanupView
from core.views.chat_history import ChatHistoryView
from core.views.profile import ProfileView
from core.views.chat import ChatView
from core.views import HomeView
from assistant.schema_views import schema_json, SwaggerUIView, ReDocUIView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls, name="admin"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("chat/", ChatView.as_view(), name="chatbot"),
    path("chat/history/", ChatHistoryView.as_view(), name="chats-history"),
    path("chat/<int:chat_id>/cleanup/", ChatCleanupView.as_view(), name="chat-cleanup"),
    # Documentación pública (vistas Django puras, sin DRF → no piden login en producción)
    path("swagger.json", schema_json, name="schema-json"),
    path("swagger/", SwaggerUIView.as_view(), name="schema-swagger-ui"),
    path("redoc/", ReDocUIView.as_view(), name="schema-redoc"),
]

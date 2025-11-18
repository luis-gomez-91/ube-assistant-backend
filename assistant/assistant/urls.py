from django.contrib import admin
from django.urls import path
from core.views.chat_cleanup import ChatCleanupView
from core.views.chat_history import ChatHistoryView
from core.views.profile import ProfileView
from core.views.chat import ChatView
from core.views import HomeView


urlpatterns = [
    path('/', HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("chat/", ChatView.as_view(), name="chatbot"),
    path("chat/history/", ChatHistoryView.as_view(), name="chats-history"),
    path("chat/<int:chat_id>/cleanup/", ChatCleanupView.as_view(), name="chat-cleanup"),

]

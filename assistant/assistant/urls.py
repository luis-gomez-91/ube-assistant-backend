from django.contrib import admin
from django.urls import path
from core.views.profile import ProfileView
from core.views.chat import ChatView
from core.views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("chat/", ChatView.as_view(), name="chat"),
]

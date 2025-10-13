import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class SimpleUser:
    """Objeto user temporal para DRF"""
    def __init__(self, user_data):
        self.id = user_data.get("id")
        self.username = user_data.get("username")
        self.email = user_data.get("email")

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username

class BackendTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None

        token = token.replace("Bearer ", "").strip()

        try:
            response = requests.get(
                "https://sga.ube.edu.ec/api/auth/verify/",
                headers={"Authorization": f"Bearer {token}"}
            )
        except requests.RequestException:
            raise AuthenticationFailed("Error conectando con UBE.")

        if response.status_code != 200:
            raise AuthenticationFailed("Token inválido en UBE.")

        user_data = response.json()
        return (SimpleUser(user_data), None)  # Ahora DRF acepta is_authenticated

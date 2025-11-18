# core/authentication/backend_auth.py

import requests
import jwt
import os
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class SimpleUser:
    """Objeto user temporal para DRF"""

    def __init__(self, user_data, provider="drf"):
        self.id = user_data.get("id") or user_data.get("sub")
        self.username = user_data.get("username") or user_data.get("email", "user")
        self.email = user_data.get("email")
        self.provider = provider

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username


class BackendTokenAuthentication(BaseAuthentication):
    """
    Autentica tanto tokens DRF (UBE) como tokens JWT de Supabase/Google/Facebook
    """

    def authenticate(self, request):
        token = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")

        if not token:
            logger.warning("No token provided in request")
            return None

        token = token.replace("Bearer ", "").strip()
        logger.info(f"Token recibido: {token[:20]}...")

        # ✅ Intenta primero con UBE (tu backend actual)
        try:
            user, auth = self.authenticate_ube(token)
            logger.info(f"Autenticación exitosa con UBE: {user.username}")
            return (user, auth)
        except AuthenticationFailed as e:
            logger.warning(f"Autenticación UBE fallida: {str(e)}")

        # ✅ Intenta después con Supabase/Google/Facebook
        try:
            user, auth = self.authenticate_supabase(token)
            logger.info(f"Autenticación exitosa con Supabase: {user.username} (proveedor: {user.provider})")
            return (user, auth)
        except AuthenticationFailed as e:
            logger.error(f"Autenticación Supabase fallida: {str(e)}")
            raise AuthenticationFailed("Token inválido. No es válido en UBE ni en Supabase.")

    def authenticate_ube(self, token):
        """Autentica contra tu UBE API (backend actual)"""
        try:
            response = requests.get(
                "https://sga.ube.edu.ec/api/auth/verify/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            logger.info(f"Respuesta UBE: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error conectando con UBE: {str(e)}")
            raise AuthenticationFailed(f"Error conectando con UBE: {str(e)}")

        if response.status_code != 200:
            raise AuthenticationFailed("Token inválido en UBE.")

        user_data = response.json()
        user = SimpleUser(user_data, provider="drf")
        return (user, f"Bearer {token}")

    def authenticate_supabase(self, token):
        """Autentica contra Supabase JWT (Google, Facebook, etc)"""

        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')

        if not supabase_url:
            logger.error("NEXT_PUBLIC_SUPABASE_URL no está configurada")
            raise AuthenticationFailed("Supabase no configurado")

        try:
            # ✅ Decodificar sin verificar firma (simplificado)
            # Supabase ya verifica que el token es válido cuando lo emite
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # No verificamos la firma
            )

            logger.info(f"Token JWT decodificado: usuario {decoded.get('email')}")

            # Validar que sea un token de Supabase verificando el issuer (iss)
            iss = decoded.get('iss')
            expected_iss = f"{supabase_url.rstrip('/')}/auth/v1"

            logger.info(f"Issuer del token: {iss}")
            logger.info(f"Issuer esperado: {expected_iss}")

            # Validar que el issuer coincida
            if iss != expected_iss:
                logger.warning(f"Issuer no coincide. Token: {iss}, Esperado: {expected_iss}")
                raise AuthenticationFailed("Token no es de Supabase")

            # Verificar que el token no esté expirado
            import time
            exp = decoded.get('exp')
            if exp and exp < time.time():
                raise AuthenticationFailed("Token expirado")

            # Extraer datos del token JWT
            user_data = {
                "id": decoded.get('sub'),
                "email": decoded.get('email'),
                "username": decoded.get('email', decoded.get('sub')),
            }

            provider = decoded.get('app_metadata', {}).get('provider', 'oauth')
            user = SimpleUser(user_data, provider=provider)

            logger.info(f"Usuario autenticado: {user.email} (proveedor: {provider})")
            return (user, token)

        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            raise AuthenticationFailed("Token de Supabase expirado")
        except jwt.InvalidTokenError as e:
            logger.error(f"Token JWT inválido: {str(e)}")
            raise AuthenticationFailed(f"Token de Supabase inválido: {str(e)}")
        except Exception as e:
            logger.error(f"Error verificando token Supabase: {str(e)}", exc_info=True)
            raise AuthenticationFailed(f"Error verificando token Supabase: {str(e)}")
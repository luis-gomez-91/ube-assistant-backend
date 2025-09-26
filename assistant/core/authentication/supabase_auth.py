# from supabase import create_client
# from django.conf import settings
# from django.contrib.auth.models import User
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# class SupabaseAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         token = request.headers.get("Authorization")
#         if not token:
#             return None
#         token = token.replace("Bearer ", "")

#         try:
#             user_info = supabase.auth.get_user(token)
#         except Exception:
#             raise AuthenticationFailed("Token inválido en Supabase.")

#         if not user_info or not user_info.user:
#             raise AuthenticationFailed("Usuario no válido en Supabase.")

#         email = user_info.user.email
#         user, _ = User.objects.get_or_create(username=email, defaults={"email": email})
#         return (user, None)

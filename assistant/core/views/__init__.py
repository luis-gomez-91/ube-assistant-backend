from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

class HomeView(APIView):
    renderer_classes = [JSONRenderer]  # <- Fuerza JSON

    def get(self, request):
        return Response({
            'status': 'success',
            'description': 'UBE Assistant es una aplicación backend desarrollada en Django que centraliza la autenticación y el acceso a los datos de estudiantes y usuarios de la plataforma UBE, así como la gestión de chats. La app permite verificar tokens de acceso emitidos por UBE y ofrece soporte para autenticación con servicios externos como Google, Facebook y otros mediante Supabase Auth. Además, almacena los chats de usuarios provenientes de otros proyectos Django o de Supabase Auth, facilitando la integración de servicios de mensajería y la interoperabilidad entre plataformas.',
            'characteristics': [
                "Validación de tokens emitidos por el sistema UBE.",
                "Autenticación con proveedores externos (Google, Facebook, Supabase Auth).",
                "Almacenamiento y gestión de chats de usuarios.",
                "Endpoints RESTful que devuelven datos en formato JSON.",
                "Arquitectura modular, escalable y segura.",
                "Compatible con Postman y cualquier cliente HTTP para pruebas o integración.",
                "Seguridad mediante autenticación basada en token y DRF.",
            ]
        })

"""
Vistas públicas para la documentación OpenAPI (sin auth DRF).
Evita que en producción Swagger/ReDoc redirijan a Django Login.
"""
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.request import Request as DRFRequest
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.app_settings import swagger_settings
from drf_yasg.codecs import OpenAPICodecJson


def schema_json(request):
    """Sirve el schema OpenAPI en JSON. Vista Django pura, sin DRF."""
    info = openapi.Info(
        title="UBE Assistant API",
        default_version="v1",
        description="API del backend UBE Assistant: autenticación, chat con IA, perfil y gestión de conversaciones.",
    )
    generator_class = swagger_settings.DEFAULT_GENERATOR_CLASS
    generator = generator_class(info, "", None, None, None)
    drf_request = DRFRequest(request)
    schema = generator.get_schema(request=drf_request, public=True)
    if schema is None:
        return HttpResponse("{}", content_type="application/json")
    codec = OpenAPICodecJson([])
    body = codec.encode(schema)
    return HttpResponse(body, content_type="application/json")


class SwaggerUIView(TemplateView):
    template_name = "docs/swagger_ui.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schema_url"] = "/swagger.json"
        return context


class ReDocUIView(TemplateView):
    template_name = "docs/redoc_ui.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schema_url"] = "/swagger.json"
        return context

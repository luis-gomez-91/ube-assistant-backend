"""
Utilidad para crear argumentos de cliente HTTP para ChatGoogleGenerativeAI.
Permite desactivar la verificación SSL cuando se está detrás de un proxy
corporativo con certificado autofirmado (CERTIFICATE_VERIFY_FAILED).
"""
import ssl
from django.conf import settings


def get_gemini_client_args():
    """
    Retorna client_args para pasar a ChatGoogleGenerativeAI.
    Si GEMINI_DISABLE_SSL_VERIFY está activo, incluye un contexto SSL
    que no verifica certificados (solo para entornos controlados/proxy corporativo).
    """
    if not getattr(settings, "GEMINI_DISABLE_SSL_VERIFY", False):
        return {}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return {"verify": ctx}

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG")

# En producción (Railway): ALLOWED_HOSTS=tu-app.railway.app o * para aceptar el dominio que asigne Railway
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS").split(",") if h.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'core',
    'adrf',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'assistant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'assistant.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Railway inyecta DATABASE_URL al conectar Postgres. Localmente usa variables o valores por defecto.
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        default=os.getenv("DATABASE_URL"),
    )
}

# Orígenes permitidos para CORS. En Railway: CORS_ALLOWED_ORIGINS=https://tu-front.vercel.app,https://tu-app.railway.app
CORS_ALLOWED_ORIGINS = [
    h.strip() for h in os.getenv("CORS_ALLOWED_ORIGINS").split(",") if h.strip()
]

# Necesario para HTTPS en Railway (Django comprueba origen en POST)
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.strip()}" for h in os.getenv("ALLOWED_HOSTS", "").split(",")
    if h.strip() and not h.strip().startswith("127.")
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# postgresql://postgres.ystetegmatjetchztrfx:[YOUR-PASSWORD]@aws-1-us-east-2.pooler.supabase.com:6543/postgres


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EXTERNAL_DJANGO_URL = "https://sga.ube.edu.ec"
SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_KEY = "super_secret_key"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Desactivar verificación SSL para Gemini (útil detrás de proxy corporativo con cert autofirmado)
GEMINI_DISABLE_SSL_VERIFY = os.getenv("GEMINI_DISABLE_SSL_VERIFY", "false").lower() in ("1", "true", "yes")
API_UBE_URL = os.getenv("API_UBE_URL")


# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#         "api.auth_backends.ExternalDjangoAuthentication",
#         "api.supabase_auth.SupabaseAuthentication",
#     ],
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'core.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

os.environ.setdefault('NEXT_PUBLIC_SUPABASE_URL', 'https://ystetegmatjetchztrfx.supabase.co')
os.environ.setdefault('NEXT_PUBLIC_SUPABASE_ANON_KEY', os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))

# O si lo prefieres, directamente:
if not os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'):
    raise ValueError("NEXT_PUBLIC_SUPABASE_ANON_KEY no está configurada en el .env")

UBE_PROVIDER_ID = 2
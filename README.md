# UBE Assistant Backend

**UBE Assistant** es un backend desarrollado en Django que centraliza la autenticación y gestión de usuarios y chats para plataformas educativas. Integra agentes conversacionales (LangChain, Gemini), permite verificar tokens emitidos por UBE y ofrece interoperabilidad con Supabase Auth.

---

## Características

- Validación de tokens emitidos por UBE (`access token`) desde otros proyectos.
- Autenticación con proveedores externos (Google, Facebook, Supabase Auth).
- Almacenamiento y gestión de chats de usuarios (Django / Supabase).
- Chat con IA: clasificación de intención y agentes por categoría (ventas, FAQ, soporte TI, información pública).
- Endpoints REST en JSON; compatible con Postman y clientes HTTP.
- Despliegue listo para Railway (Postgres, variables de entorno, Gunicorn).

---

## Requisitos

- Python 3.13+
- PostgreSQL (local o servicio externo)

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio-url>
cd ube-assistant-backend
```

### 2. Entorno virtual

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### 3. Dependencias

```bash
pip install -r requirements.txt
```

### 4. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

| Variable | Descripción | Ejemplo (desarrollo) |
|----------|-------------|----------------------|
| `SECRET_KEY` | Clave secreta de Django | Una cadena larga y aleatoria |
| `DEBUG` | Modo debug | `true` (local) / `false` (producción) |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:pass@localhost:5432/dbname` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS (separados por coma) | `http://localhost:3000,http://127.0.0.1:3000` |
| `GEMINI_API_KEY` | API key de Google Gemini | Tu clave de [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_DISABLE_SSL_VERIFY` | Desactivar verificación SSL para Gemini (proxy corporativo) | `false` |
| `API_UBE_URL` | URL base de la API UBE | `https://sga.ube.edu.ec/api/` |
| `NEXT_PUBLIC_SUPABASE_URL` | URL del proyecto Supabase | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon key de Supabase | Clave anónima del proyecto |

Ejemplo mínimo para desarrollo local:

```env
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/assistant_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
GEMINI_API_KEY=tu-api-key-gemini
API_UBE_URL=https://sga.ube.edu.ec/api/
NEXT_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu-anon-key
```

### 5. Migraciones y servidor

El proyecto Django está dentro de la carpeta `assistant/`. Ejecutar desde la raíz o desde `assistant/`:

```bash
cd assistant
python manage.py migrate
python manage.py runserver
```

El servidor queda en **http://127.0.0.1:8000/**.

---

## Despliegue en Railway

1. Conectar el repositorio desde GitHub en Railway.
2. Añadir el plugin **Postgres** al proyecto (Railway inyecta `DATABASE_URL`).
3. Configurar en Railway las mismas variables de entorno, con valores de producción:
   - `SECRET_KEY`: clave segura nueva.
   - `DEBUG`: `false`.
   - `ALLOWED_HOSTS`: dominio asignado por Railway (ej. `tu-app.railway.app`).
   - `CORS_ALLOWED_ORIGINS`: URL del frontend en producción (ej. `https://tu-front.vercel.app`).
   - `GEMINI_API_KEY`, `API_UBE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
4. El **Procfile** en la raíz define el comando de inicio (migraciones + Gunicorn). Railway lo usará automáticamente.

---

## Endpoints principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Home; retorna JSON de estado. |
| `/profile/` | GET | Perfil del usuario (header: `Authorization: Bearer <access-token>`). |
| `/chat/` | POST | Enviar mensaje al chatbot (body: `message`, `provider`, `chat_id` opcional). |
| `/chat/history/` | GET | Historial de chats. |
| `/chat/<id>/cleanup/` | POST | Limpiar contexto de un chat. |
| `/swagger/` | GET | Documentación interactiva de la API (estilo FastAPI). |
| `/redoc/` | GET | Documentación ReDoc de la API. |
| `/admin/` | GET | Panel de administración Django. |

---

## Estructura del proyecto

```
ube-assistant-backend/
├── assistant/                 # Proyecto Django
│   ├── assistant/             # Settings y URLs
│   │   ├── settings.py
│   │   └── urls.py
│   ├── core/
│   │   ├── agents/            # Agentes de chat (ventas, FAQ, soporte TI, público)
│   │   ├── authentication/    # Backends de autenticación (UBE, Supabase)
│   │   ├── views/             # Vistas REST (chat, profile, history, cleanup)
│   │   ├── utils/             # Utilidades (memoria, Gemini client, etc.)
│   │   └── models.py
│   └── manage.py
├── Procfile                   # Comando de inicio para Railway
├── runtime.txt                # Python 3.13 para Railway
├── requirements.txt
└── .env                       # Variables de entorno (no subir a Git)
```

---

## Notas

- El backend no crea usuarios locales; autentica contra UBE o proveedores externos.
- Para producción, no uses `DEBUG=true` ni expongas `SECRET_KEY` ni las claves de API en el repositorio.

---

## Licencia

MIT License

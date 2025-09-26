# UBE Assistant Backend

**UBE Assistant** es un backend desarrollado en Django que centraliza la autenticación y gestión de usuarios y chats para plataformas educativas. Facilita la integración de servicios externos y permite verificar tokens emitidos por UBE, ofreciendo interoperabilidad entre proyectos Django y Supabase Auth.

---

## Características

- Validación de tokens emitidos por UBE (`access token`) desde otros proyectos.
- Autenticación con proveedores externos como Google, Facebook, y Supabase Auth.
- Almacenamiento y gestión de chats de usuarios provenientes de otros Django o Supabase.
- Endpoints RESTful que devuelven datos en formato JSON.
- Arquitectura modular y escalable.
- Seguridad mediante autenticación basada en token usando Django REST Framework (DRF).
- Compatible con Postman y cualquier cliente HTTP para pruebas o integración.

---

## Instalación

1. Clonar el repositorio:
```
git clone <tu-repositorio-url>
cd ube-assistant-backend

2. Crear y activar un entorno virtual:
```
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```
pip install -r requirements.txt
```

4. Configurar variables de entorno (puedes usar un .env):
```
env
DEBUG=True
SECRET_KEY=<tu-secret-key>
SUPABASE_URL=<url-supabase>
SUPABASE_KEY=<key-supabase>
EXTERNAL_UBE_URL=https://sga.ube.edu.ec/api
```

5. Aplicar migraciones:
```
Copiar código
python manage.py migrate
```

6. Ejecutar el servidor:
```
python manage.py runserver
```
 ---

## Uso

- Ver perfil del usuario:
Endpoint: /profile/
Método: GET
Requiere enviar en el header:
```
http
Authorization: Bearer <access-token>
```

- Home:
Endpoint: /
Retorna un JSON simple de estado:
```
json
{"status": "success"}
```
 ---

## Estructura del proyecto

```
core/
  ├── views/           # Endpoints REST
  ├── authentication/  # Backends de autenticación (UbeToken, Supabase, etc.)
  ├── models.py        # Modelos de chats, providers, etc.

```

---

## Notas
- Este backend no crea usuarios locales, solo autentica y gestiona datos de usuarios existentes en UBE o proveedores externos.
- Está pensado para integrarse con otros proyectos Django y clientes REST.

---

## Contribuciones
Las contribuciones son bienvenidas. Por favor crea un fork y envía pull requests.

---

## Licencia
MIT License
```
---

Si quieres, puedo hacer también una **versión más resumida estilo “one-page README”** que sea más llamativa y lista para GitHub sin tanta configuración técnica.  
```

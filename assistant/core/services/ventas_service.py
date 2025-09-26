# core/services/ventas_service.py

from argo import Message
from core.agents.ventas_agent import initialize_agent
from core.serializers.ventas.carreras_serializer import *
from core.serializers.ventas.malla_serializers import *
from core.serializers.ventas.grupos_serializer import *

agent = initialize_agent()

async def get_ai_response(user_message: str) -> str:
    """
    Envía un mensaje al agente Argo y devuelve la respuesta generada por la IA.
    """
    ctx = await agent.chat(Message.user(user_message))
    reply = ctx.last_message().content if ctx.last_message() else "No hubo respuesta."
    return reply

import requests
from assistant.settings import API_UBE_URL
import httpx


async def fetch_carreras() -> CarrerasSerializer:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_UBE_URL}carreras")
        r.raise_for_status()
        data = r.json()
        r.raise_for_status()
        data = r.json()
        serializer = CarrerasSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer


async def fetch_grupos(id_carrera: int) -> GruposSerializer:
    response = requests.get(f"{API_UBE_URL}grupos/{id_carrera}")
    response.raise_for_status()
    data = response.json()
    serializer = GruposSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer

async def fetch_malla(id_carrera: int) -> MallaSerializer:
    response = requests.get(f"{API_UBE_URL}malla/{id_carrera}")
    response.raise_for_status()
    data = response.json()
    serializer = MallaSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer

# async def matricular():
#     response = requests.post(f"{API_UBE_URL}matricular", json={"aprove": True})
#     response.raise_for_status()
#     data = response.json()
#     malla_instance = Matricular(**data)
#     return malla_instance
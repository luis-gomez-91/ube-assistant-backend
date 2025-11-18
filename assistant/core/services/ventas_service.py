# core/services/ventas_service.py
from typing import List

import httpx
from assistant.settings import API_UBE_URL
from schemas.ventas.carreras import CarrerasModel, DetalleCarreraModel
from schemas.ventas.grupos import GruposModel
from schemas.ventas.malla import MallaModel
from pydantic import TypeAdapter

adapter = TypeAdapter(List[CarrerasModel])

async def fetch_carreras() -> List[CarrerasModel]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}ventas/carreras/")
        response.raise_for_status()
        carreras_data = response.json()
        return adapter.validate_python(carreras_data)

async def fetch_grupos(id_carrera: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}ventas/grupos/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        grupos_instance = GruposModel(**data)
        return grupos_instance

async def fetch_malla(id_carrera: int) -> MallaModel:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}ventas/malla/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        malla_instance = MallaModel(**data)
        return malla_instance

async def fetch_detalle_carrera(id_carrera: int) -> DetalleCarreraModel:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}ventas/carreras/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        print(data)
        detalle_instance = DetalleCarreraModel(**data)
        return detalle_instance
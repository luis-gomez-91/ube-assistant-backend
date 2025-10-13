# core/services/ventas_service.py
import httpx
import requests
from assistant.settings import API_UBE_URL
from schemas.ventas.carreras import CarrerasModel, CarreraDetalleModel
from schemas.ventas.grupos import GruposModel, GrupoDataModel
from schemas.ventas.malla import MallaModel


# def fetch_carreras() -> DataCarrerasModel:
#     response = requests.get(f"{API_UBE_URL}carreras")
#     response.raise_for_status()
#     carreras_data = response.json()
#     carreras_instance = CarrerasModel(
#         status=carreras_data["status"],
#         data=DataCarrerasModel(**carreras_data["data"])
#     )
#     return carreras_instance.data
#
# def fetch_grupos(id_carrera: int) -> list[GrupoDataModel]:
#     response = requests.get(f"{API_UBE_URL}grupos/{id_carrera}")
#     response.raise_for_status()
#     data = response.json()
#     grupos_instance = GruposModel(**data)
#     return grupos_instance.data
#
# def fetch_malla(id_carrera: int):
#     response = requests.get(f"{API_UBE_URL}malla/{id_carrera}")
#     response.raise_for_status()
#     data = response.json()
#     malla_instance = MallaModel(**data)
#     return malla_instance

# async def matricular():
#     response = requests.post(f"{API_UBE_URL}matricular", json={"aprove": True})
#     response.raise_for_status()
#     data = response.json()
#     malla_instance = Matricular(**data)
#     return malla_instance

async def fetch_carreras() -> CarrerasModel:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}carreras/")
        response.raise_for_status()
        carreras_data = response.json()
        carreras_instance = CarrerasModel(**carreras_data)
        return carreras_instance

async def fetch_grupos(id_carrera: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}grupos/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        grupos_instance = GruposModel(**data)
        return grupos_instance

async def fetch_malla(id_carrera: int) -> MallaModel:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}malla/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        malla_instance = MallaModel(**data)
        return malla_instance

async def fetch_detalle_carrera(id_carrera: int) -> CarreraDetalleModel:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_UBE_URL}carreras/{id_carrera}/")
        response.raise_for_status()
        data = response.json()
        print(data)
        detalle_instance = CarreraDetalleModel(**data)
        return detalle_instance
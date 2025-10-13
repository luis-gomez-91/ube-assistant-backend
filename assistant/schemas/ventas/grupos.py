from pydantic import BaseModel
from typing import List
from schemas import Response


class GrupoDataModel(BaseModel):
    carrera: str
    nombre: str
    fecha_inicio: str
    fecha_fin: str
    capacidad: int
    sesion: str
    modalidad: str
    nivel: str

class GruposModel(Response):
    data: List[GrupoDataModel]
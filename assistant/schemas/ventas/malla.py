from pydantic import BaseModel
from typing import List, Optional
from schemas import Response


class AsignaturaModel(BaseModel):
    asignatura: str
    horas: int | float
    creditos: Optional[int] = None

class DataMallaModel(BaseModel):
    nivel_malla: str
    asignaturas: List[AsignaturaModel]

class MallaModel(Response):
    data: List[DataMallaModel]

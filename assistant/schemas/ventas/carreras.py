from pydantic import BaseModel
from typing import List, Optional


class PreciosModel(BaseModel):
    inscripcion: float = None
    matricula: float = None
    numero_cuotas: int = None
    homologacion: Optional[float] = None

class CarreraBaseModel(BaseModel):
    id: int
    nombre: str
    titulo: str

class CarreraDetalleModel(CarreraBaseModel):
    sesiones: List[str]
    modalidades: List[str]
    precios: Optional[PreciosModel] = None

class CarrerasModel(BaseModel):
    grado: List[CarreraBaseModel]
    postgrado: List[CarreraBaseModel]
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import re


class CarreraModel(BaseModel):
    id: int
    nombre: str

class AreaEstudioModel(BaseModel):
    nombre: str
    carreras: List[CarreraModel]

class CarrerasModel(BaseModel):
    tipo: str
    areas: List[AreaEstudioModel]



class InfoCarreraModel(BaseModel):
    id: int
    codigo: int
    nombre: str
    titulo: str
    campo_llaboral: str
    numero_periodos: Optional[int]
    area_estudio: str
    descuento_carrera: Optional[float]
    descuento_nivel: Optional[float]


class PreciosCarreraModel(BaseModel):
    inscripcion: float
    matricula: Optional[float]
    cuota: float
    num_cuota: int
    pre: Optional[float]

class DetalleCarreraModel(BaseModel):
    general: InfoCarreraModel
    precios: PreciosCarreraModel
    modalidades: List[str]
    descuentos: Optional[str] = None


class DatosMatriculaModel(BaseModel):
    """Modelo para validar datos de matrícula"""
    nombre_carrera: str
    grupo: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    correo: EmailStr
    numero_celular: str
    tipo_sangre: Optional[str] = None
    nacionalidad: Optional[str] = "Ecuatoriana"
    raza: Optional[str] = None

    @validator('numero_celular')
    def validar_celular(cls, v):
        # Validar formato ecuatoriano
        if not re.match(r'^\+593\d{9}$', v):
            raise ValueError('El número debe tener formato +593XXXXXXXXX')
        return v
"""
Módulo Modelos (models.py)
Define esquemas de Pydantic y adaptadores para ObjectId de MongoDB - Caso: Alquiler de Equipos.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema


class ObjectIdPydanticAnnotation:
    """Adaptador para validar y serializar ObjectId de MongoDB en Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("ID inválido MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[str, ObjectIdPydanticAnnotation]


class EquipoRentaBase(BaseModel):
    equipo_renta: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre o referencia del equipo alquilado",
        example="Taladro Percutor Industrial Bosch"
    )
    cliente: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre completo del cliente que alquila el equipo",
        example="Carlos Andrés Martínez"
    )
    dias_alquiler: int = Field(
        ...,
        ge=1,
        description="Cantidad de días contratados para el alquiler",
        example=5
    )
    devuelto: bool = Field(
        default=False,
        description="Indica si el equipo ya fue devuelto por el cliente"
    )


class EquipoRentaCreate(EquipoRentaBase):
    """Modelo utilizado para recibir solicitudes POST en FastAPI"""
    pass


class EquipoRentaUpdate(BaseModel):
    """Modelo para solicitudes PUT (Campos opcionales para edición parcial)"""
    equipo_renta: Optional[str] = Field(None, min_length=3, max_length=150)
    cliente: Optional[str] = Field(None, min_length=3, max_length=150)
    dias_alquiler: Optional[int] = Field(None, ge=1)
    devuelto: Optional[bool] = None


class EquipoRenta(EquipoRentaBase):
    """Modelo completo de respuesta que incluye el ID de MongoDB y fecha de registro"""
    id: PyObjectId = Field(alias="_id", description="Identificador único ObjectId de MongoDB")
    fecha_registro: datetime = Field(default_factory=datetime.now, description="Fecha y hora del alquiler")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "654321789abcdef012345678",
                "equipo_renta": "Taladro Percutor Industrial Bosch",
                "cliente": "Carlos Andrés Martínez",
                "dias_alquiler": 5,
                "devuelto": False,
                "fecha_registro": "2026-11-19T08:30:00"
            }
        }
    )
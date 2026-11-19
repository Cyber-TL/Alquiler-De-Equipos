"""
Módulo Principal de la Aplicación (main.py)
API RESTful asíncrona con FastAPI y Motor - Caso: Alquiler de Equipos (Thomas Leyton).
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
from datetime import datetime

from models import EquipoRenta, EquipoRentaCreate, EquipoRentaUpdate
from database import coleccion_equipos, verificar_conexion

app = FastAPI(
    title="API Alquiler de Equipos - SENA ADSO",
    description="API RESTful asíncrona con FastAPI y MongoDB para gestión de renta de equipos.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()



@app.get("/", tags=["Raíz"])
async def root():
    return {
        "mensaje": "Bienvenido a la API de Alquiler de Equipos (Thomas Leyton - SENA ADSO)",
        "documentacion": "/docs"
    }


@app.post(
    "/equipos",
    response_model=EquipoRenta,
    status_code=status.HTTP_201_CREATED,
    tags=["Alquiler de Equipos"],
    summary="Registrar un nuevo alquiler de equipo en MongoDB"
)
async def create_equipo_renta(renta_in: EquipoRentaCreate):
    """
    Registra un nuevo alquiler en la colección 'renta_equipos':
    - Verifica que el mismo equipo no tenga un alquiler activo sin devolver (HTTP 400).
    - Asigna fecha de registro automática.
    """
    alquiler_activo = await coleccion_equipos.find_one({
        "equipo_renta": renta_in.equipo_renta,
        "devuelto": False
    })
    if alquiler_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El equipo '{renta_in.equipo_renta}' ya se encuentra alquilado y no ha sido devuelto."
        )

    nuevo_registro = renta_in.model_dump()
    nuevo_registro["fecha_registro"] = datetime.now()

    resultado = await coleccion_equipos.insert_one(nuevo_registro)
    registro_creado = await coleccion_equipos.find_one({"_id": resultado.inserted_id})
    return registro_creado


@app.get(
    "/equipos",
    response_model=List[EquipoRenta],
    status_code=status.HTTP_200_OK,
    tags=["Alquiler de Equipos"],
    summary="Listar todos los alquileres de equipos"
)
async def get_equipos_renta():
    """Recupera asíncronamente todos los documentos de la colección 'renta_equipos'."""
    registros = []
    cursor = coleccion_equipos.find()
    async for documento in cursor:
        registros.append(documento)
    return registros


@app.get(
    "/equipos/{id}",
    response_model=EquipoRenta,
    status_code=status.HTTP_200_OK,
    tags=["Alquiler de Equipos"],
    summary="Buscar registro de alquiler por ObjectId"
)
async def get_equipo_por_id(id: str):
    """Busca un alquiler específico por su ObjectId de MongoDB."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB."
        )

    registro = await coleccion_equipos.find_one({"_id": ObjectId(id)})
    if registro:
        return registro

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El registro de alquiler con ID '{id}' no fue encontrado."
    )


@app.put(
    "/equipos/{id}",
    response_model=EquipoRenta,
    status_code=status.HTTP_200_OK,
    tags=["Alquiler de Equipos"],
    summary="Actualizar datos o marcar equipo como devuelto"
)
async def update_equipo_renta(id: str, renta_update: EquipoRentaUpdate):
    """Actualiza parcialmente un registro de alquiler por su _id."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    datos_a_actualizar = renta_update.model_dump(exclude_unset=True)

    if len(datos_a_actualizar) >= 1:
        resultado = await coleccion_equipos.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos_a_actualizar}
        )

        if resultado.modified_count == 1 or resultado.matched_count == 1:
            registro_modificado = await coleccion_equipos.find_one({"_id": ObjectId(id)})
            return registro_modificado

    registro_existente = await coleccion_equipos.find_one({"_id": ObjectId(id)})
    if registro_existente:
        return registro_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. El registro con ID '{id}' no existe."
    )


@app.delete(
    "/equipos/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Alquiler de Equipos"],
    summary="Eliminar registro de alquiler de MongoDB"
)
async def delete_equipo_renta(id: str):
    """Elimina permanentemente un registro de alquiler por su ObjectId."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    resultado = await coleccion_equipos.delete_one({"_id": ObjectId(id)})

    if resultado.deleted_count == 1:
        return {"mensaje": f"Registro de alquiler con ID '{id}' eliminado exitosamente de MongoDB."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. El registro con ID '{id}' no existe en la base de datos."
    )
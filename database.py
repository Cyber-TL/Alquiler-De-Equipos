"""
Módulo de Base de Datos (database.py)
Gestiona la conexión asíncrona a MongoDB utilizando Motor para Alquiler de Equipos.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="adso_db")

# Cliente asíncrono de MongoDB
client = AsyncIOMotorClient(MONGODB_URL)

# Referencia a la base de datos documental
database = client[DATABASE_NAME]

# Colección asignada en la guía: renta_equipos
coleccion_equipos = database["renta_equipos"]

async def verificar_conexion():
    """Función de comprobación de estado de la conexión al iniciar la API"""
    try:
        await client.admin.command('ping')
        print(f"Conexión exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}' | Colección: 'renta_equipos'")
    except Exception as e:
        print(f"Error de conexión a MongoDB: {e}")
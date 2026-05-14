from fastapi import FastAPI
from app.api import audit_logs, auth, familias, focos_sanitarios, personas, users, zonas
from app.api import bodegas, refugios
from app.api import configuracion_puntaje, planes_distribucion
from app.api import entregas

from app.api import (
    audit_logs,
    auth,
    bodegas,
    configuracion_puntaje,
    familias,
    focos_sanitarios,
    inventario,
    personas,
    planes_distribucion,
    refugios,
    reportes,
    recursos,
    users,
    zonas,
)
from app.api.donantes import router as donantes_router
from app.core.audit_middleware import AuditMiddleware
from app.domain.models.donante import Donante
from app.domain.models.movimiento_inventario import MovimientoInventario
from app.domain.models.persona import Persona
from app.domain.models.user import User
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine

app = FastAPI()
app.add_middleware(AuditMiddleware)


@app.on_event("startup")
async def startup():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(donantes_router)
app.include_router(refugios.router)
app.include_router(bodegas.router)
app.include_router(recursos.router)
app.include_router(inventario.router)
app.include_router(familias.router)
app.include_router(configuracion_puntaje.router)
app.include_router(planes_distribucion.router)
app.include_router(audit_logs.router)
app.include_router(focos_sanitarios.router)
app.include_router(reportes.router)
app.include_router(entregas.router)

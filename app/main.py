from fastapi import FastAPI
from app.api import audit_logs, auth, familias, focos_sanitarios, personas, users, zonas
from app.api import bodegas, refugios
from app.api import configuracion_puntaje, planes_distribucion

from app.api import (
    audit_logs,
    auth,
    configuracion_puntaje,
    familias,
    focos_sanitarios,
    personas,
    planes_distribucion,
    reportes,
    recursos,
    users,
    zonas,
)
from app.core.audit_middleware import AuditMiddleware

app = FastAPI()
app.add_middleware(AuditMiddleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(refugios.router)
app.include_router(bodegas.router)
app.include_router(recursos.router)
app.include_router(familias.router)
app.include_router(configuracion_puntaje.router)
app.include_router(planes_distribucion.router)
app.include_router(audit_logs.router)
app.include_router(focos_sanitarios.router)
app.include_router(reportes.router)

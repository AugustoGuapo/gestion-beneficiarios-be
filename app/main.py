from fastapi import FastAPI
from app.api import users
from app.api import personas
from app.api import zonas
from app.api import auth
from app.api import familias
from app.api import configuracion_puntaje
from app.api import planes_distribucion
from app.api import indicadores

from app.api import audit_logs, auth, focos_sanitarios, personas, users, zonas
from app.core.audit_middleware import AuditMiddleware

app = FastAPI()
app.add_middleware(AuditMiddleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(familias.router)
app.include_router(configuracion_puntaje.router)
app.include_router(planes_distribucion.router)
app.include_router(audit_logs.router)
app.include_router(focos_sanitarios.router)
app.include_router(indicadores.router)

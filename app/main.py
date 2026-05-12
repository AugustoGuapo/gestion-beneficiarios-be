from fastapi import FastAPI
from app.api import users
from app.api import personas
from app.api import zonas
from app.api import auth
from app.api import familias
from app.api import configuracion_puntaje
from app.api import planes_distribucion

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(familias.router)
app.include_router(configuracion_puntaje.router)
app.include_router(planes_distribucion.router)

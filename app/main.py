from fastapi import FastAPI
from app.api import users
from app.api import personas
from app.api import zonas
from app.api import auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)

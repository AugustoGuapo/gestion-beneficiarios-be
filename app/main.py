from fastapi import FastAPI

from app.api import auth, personas, recursos, users, zonas

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(recursos.router)

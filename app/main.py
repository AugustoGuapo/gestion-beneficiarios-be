from fastapi import FastAPI

from app.api import users
from app.api import personas
from app.api import zonas
from app.api import auth

from app.api.donantes import router as donantes_router

from app.domain.models.user import User
from app.domain.models.persona import Persona
from app.domain.models.donante import Donante

from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine

app = FastAPI()


@app.on_event("startup")
async def startup():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(zonas.router)
app.include_router(donantes_router)
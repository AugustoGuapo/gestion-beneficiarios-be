from pydantic import BaseModel


class PersonaResponse(BaseModel):
    id_persona: int
    nombre: str
    edad: int | None
    es_nino: bool
    es_anciano: bool
    es_embarazada: bool

    class Config:
        from_attributes = True


class PersonaCreate(BaseModel):
    nombre: str
    edad: int | None = None
    es_nino: bool = False
    es_anciano: bool = False
    es_embarazada: bool = False
from pydantic import BaseModel


class ZonaResponse(BaseModel):
    id_zona: int
    nombre: str

    class Config:
        from_attributes = True


class ZonaCreate(BaseModel):
    nombre: str
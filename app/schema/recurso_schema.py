from pydantic import BaseModel


class RecursoResponse(BaseModel):
    id_recurso: int
    nombre: str
    categoria: str
    unidad: str
    peso_unitario: float

    class Config:
        from_attributes = True


class RecursoCreate(BaseModel):
    nombre: str
    categoria: str
    unidad: str
    peso_unitario: float

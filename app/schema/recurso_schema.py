from pydantic import BaseModel


class RecursoResponse(BaseModel):
    id_recurso: int
    nombre: str
    peso_unitario_kg: float
    id_origen: int | None = None

    class Config:
        from_attributes = True


class RecursoCreate(BaseModel):
    nombre: str
    peso_unitario_kg: float
    id_origen: int | None = None

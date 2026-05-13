from pydantic import BaseModel
from typing import List


class DonacionRecursoItem(BaseModel):
    recurso_id: int
    cantidad: float


class DonacionCreate(BaseModel):
    referencia: str | None = None
    items: List[DonacionRecursoItem]


class DonacionResponse(BaseModel):
    id_donacion: int
    codigo: str | None
    referencia: str | None

    class Config:
        from_attributes = True

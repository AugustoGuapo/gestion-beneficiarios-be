from pydantic import BaseModel


class InventarioResponse(BaseModel):
    id_inventario: int
    recurso_id: int
    cantidad: float

    class Config:
        from_attributes = True


class InventarioCreate(BaseModel):
    recurso_id: int
    cantidad: float

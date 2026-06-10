from pydantic import BaseModel


class DonanteBase(BaseModel):
    nombre: str
    tipo_donante: str


class DonanteCreate(DonanteBase):
    pass


class DonanteResponse(DonanteBase):
    id_donante: int

    class Config:
        from_attributes = True
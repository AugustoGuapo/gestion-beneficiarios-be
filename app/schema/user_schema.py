from pydantic import BaseModel


class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    rol: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    nombre: str
    rol: str
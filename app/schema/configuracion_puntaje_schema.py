from pydantic import BaseModel


class ConfiguracionPuntajeResponse(BaseModel):
    id_config: int
    clave: str
    valor: float
    descripcion: str | None

    class Config:
        from_attributes = True


class ConfiguracionPuntajeUpdate(BaseModel):
    valor: float
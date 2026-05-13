from pydantic import BaseModel


class PersonaCreate(BaseModel):
    id_familia: int | None = None
    nombre: str
    edad: int | None = None
    es_nino: bool = False
    es_anciano: bool = False
    es_embarazada: bool = False
    tipo_documento: str | None = None
    numero_documento: str | None = None
    tiene_discapacidad: bool = False
    tiene_enfermedad_cronica: bool = False
    es_cabeza_familia: bool = False


class PersonaUpdate(BaseModel):
    id_familia: int | None = None
    nombre: str | None = None
    edad: int | None = None
    es_nino: bool | None = None
    es_anciano: bool | None = None
    es_embarazada: bool | None = None
    tipo_documento: str | None = None
    numero_documento: str | None = None
    tiene_discapacidad: bool | None = None
    tiene_enfermedad_cronica: bool | None = None
    es_cabeza_familia: bool | None = None


class PersonaResponse(BaseModel):
    id_persona: int
    id_familia: int | None
    nombre: str
    edad: int | None
    es_nino: bool
    es_anciano: bool
    es_embarazada: bool
    tipo_documento: str | None
    numero_documento: str | None
    tiene_discapacidad: bool
    tiene_enfermedad_cronica: bool
    es_cabeza_familia: bool

    class Config:
        from_attributes = True

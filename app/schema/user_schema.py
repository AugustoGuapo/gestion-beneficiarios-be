from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.core.constants import UserRole


class UserBase(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=255, description="Nombre completo del usuario")
    correo: EmailStr = Field(..., description="Email único del usuario")
    rol: UserRole = Field(default=UserRole.REGISTRADOR_DONACIONES, description="Rol del usuario")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña (mínimo 8 caracteres)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class UserUpdate(BaseModel):
    nombre_completo: str | None = Field(None, min_length=3, max_length=255)
    rol: UserRole | None = None
    activo: bool | None = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id_usuario: int
    nombre_completo: str
    correo: str
    rol: str
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    correo: EmailStr = Field(..., description="Correo del usuario")
    password: str = Field(..., description="Contraseña")


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict = Field(..., description="Datos básicos del usuario autenticado")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=100, description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nueva contraseña")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class MessageResponse(BaseModel):
    detail: str


class UserListResponse(BaseModel):
    id_usuario: int
    nombre_completo: str
    correo: str
    rol: str
    activo: bool

    class Config:
        from_attributes = True
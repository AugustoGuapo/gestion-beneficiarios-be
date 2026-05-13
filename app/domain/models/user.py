from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.infrastructure.db.base import Base


class User(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False, default="REGISTRADOR_DONACIONES")
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id_usuario}, correo={self.correo}, rol={self.rol}, activo={self.activo})>"
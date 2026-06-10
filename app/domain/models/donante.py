from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.infrastructure.db.base import Base


class Donante(Base):

    __tablename__ = "donante"

    id_donante = Column(Integer, primary_key=True, index=True)
   
    nombre = Column(String(255), nullable=False)

    tipo_donante = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            "tipo_donante",
            name="uq_nombre_tipo_donante",
        ),
    )
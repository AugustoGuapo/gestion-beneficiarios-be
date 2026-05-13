from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Familia(Base):
    __tablename__ = "familia"

    id_familia = Column(Integer, primary_key=True, index=True)
    id_representante = Column(
        Integer,
        ForeignKey("persona.id_persona", ondelete="SET NULL", onupdate="CASCADE"),
        unique=True,
        nullable=True,
    )

    representante = relationship("Persona", foreign_keys=[id_representante])

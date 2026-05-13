from sqlalchemy import Column, Date, ForeignKey, Integer

from app.infrastructure.db.base import Base


class FamiliaAlbergue(Base):
    """Relación muchos-a-muchos entre familia y albergue.

    PK compuesta (id_familia, id_albergue) según `scripts/init.sql`.
    """

    __tablename__ = "familia_albergue"

    id_familia = Column(
        Integer,
        ForeignKey("familia.id_familia", ondelete="CASCADE"),
        primary_key=True,
    )
    id_albergue = Column(
        Integer,
        ForeignKey("albergue.id_albergue", ondelete="CASCADE"),
        primary_key=True,
    )
    fecha_ingreso = Column(Date, nullable=True)

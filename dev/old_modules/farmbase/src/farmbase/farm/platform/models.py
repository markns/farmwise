from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base

# from farmbase.farm.field.models import BoundaryDefinitionActivity, Field


class Platform(Base):
    __tablename__ = "platform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships (collection names remain plural)
    fields_added: Mapped[list["Field"]] = relationship(back_populates="added_on_platform")
    boundary_activities: Mapped[list["BoundaryDefinitionActivity"]] = relationship(back_populates="platform")

    def __repr__(self):
        return f"<Platform(id={self.id}, platform_name='{self.platform_name}')>"

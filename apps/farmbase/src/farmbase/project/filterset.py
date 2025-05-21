from pydantic import Field
from sqlalchemy_filterset import (
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ..database.core import BaseFilterSet
from ..models import PaginationParams
from .models import Project


class ProjectFilterSet(BaseFilterSet[Project]):
    name = SearchFilter(Project.name)
    ordering = OrderingFilter(
        id=OrderingField(Project.id),
        name=OrderingField(Project.name),
    )


class ProjectQueryParams(PaginationParams):
    name: str | None = Field(None)

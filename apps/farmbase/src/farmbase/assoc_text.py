from __future__ import annotations

import asyncio
from typing import List, Optional

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class FarmbaseUser(Base):
    __tablename__ = "farmbase_user"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))

    projects: Mapped[List[FarmbaseUserProject]] = relationship(
        back_populates="farmbase_user",
        cascade="all, delete-orphan",
    )

    # association proxy of "projects" collection
    # to "keyword" attribute
    projects: AssociationProxy[List[Project]] = association_proxy(
        "projects",
        "project",
        creator=lambda keyword_obj: FarmbaseUserProject(project=keyword_obj),
    )

    def __init__(self, name: str):
        self.name = name


class Project(Base):
    __tablename__ = "project"
    # __table_args__ = {"schema": "tenant1"}
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column("keyword", String(64))

    user_assoc: Mapped[List["FarmbaseUserProject"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __init__(self, keyword: str):
        self.keyword = keyword

    def __repr__(self) -> str:
        return f"Keyword({self.keyword!r})"


class FarmbaseUserProject(Base):
    __tablename__ = "farmbase_user_project"
    # __table_args__ = {"schema": "tenant1"}
    farmbase_user_id: Mapped[int] = mapped_column(ForeignKey(FarmbaseUser.id), primary_key=True)
    farmbase_user: Mapped[FarmbaseUser] = relationship(back_populates="projects")

    project_id: Mapped[int] = mapped_column(ForeignKey(Project.id), primary_key=True)
    project: Mapped[Project] = relationship(back_populates="user_assoc")

    special_key: Mapped[Optional[str]] = mapped_column(String(50))


async def main():
    database_hostname = "localhost"
    database_user = "postgres"
    database_password = "VHCxiwPqpBQpi6TUFc"
    database_db = "farmbase"
    #
    # engine = create_engine(
    #     f"postgresql+psycopg2://{database_user}:{database_password}@{database_hostname}:5432/{database_db}",
    #     echo=True,
    # )
    # schema_engine = engine.execution_options(schema_translate_map={None: "tenant1"})
    # with engine.begin() as conn:
    #     conn.execute(CreateSchema("core", if_not_exists=True))
    #     conn.execute(CreateSchema("tenant1", if_not_exists=True))
    #
    # Base.metadata.create_all(schema_engine)

    engine = create_async_engine(
        f"postgresql+asyncpg://{database_user}:{database_password}@{database_hostname}:5432/{database_db}",
        echo=True,
    )
    schema_engine = engine.execution_options(schema_translate_map={None: "tenant1"})

    async_session = async_sessionmaker(
        bind=schema_engine,
        expire_on_commit=False,
    )
    #
    # async with async_session() as session:
    #     user = FarmbaseUser("mark")
    #     for kw in (Project("new_from_blammo"), Project("its_big")):
    #         user.projects.append(kw)
    #     session.add(user)
    #     await session.commit()

    async with async_session() as session:
        stmt = select(Project).options(selectinload(Project.user_assoc).selectinload(FarmbaseUserProject.farmbase_user))
        result = await session.execute(stmt)
        for project in result.scalars():
            print(project)
            for assoc in project.user_assoc:
                print(f"   {assoc.farmbase_user.name}")

    async with async_session() as session:
        stmt = select(FarmbaseUser).options(
            selectinload(FarmbaseUser.projects).selectinload(FarmbaseUserProject.project)
        )
        result = await session.execute(stmt)
        for user in result.scalars():
            print(user.name)
            for kw in user.projects:
                print(kw.keyword)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

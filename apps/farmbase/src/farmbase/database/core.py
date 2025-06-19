import functools
import re
from typing import Annotated, Any, ClassVar

from fastapi import Depends
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, object_session, sessionmaker
from sqlalchemy.sql.expression import true
from sqlalchemy_filterset import AsyncFilterSet, LimitOffsetFilter
from sqlalchemy_filterset.filtersets import Model
from sqlalchemy_utils import get_mapper
from starlette.requests import Request

from farmbase.config import settings
from farmbase.database.logging import SessionTracker


def create_db_engine(async_: bool = True, echo: bool = False):
    """
    Create a database engine by building the URL manually from settings.
    Can create either an async or a sync engine.

    Args:
        async_: If True, creates an async engine. If False, creates a sync engine.
        echo: If True, enables SQLAlchemy engine logging.
    """

    connect_args = {}
    host = settings.DATABASE_HOSTNAME
    port = settings.DATABASE_PORT

    # If using a Unix socket, move the path to connect_args
    # and clear the host/port for the main URL object.
    if host.startswith('/'):
        connect_args["host"] = host
        host = None
        port = None

    # Determine the correct drivername based on the async_ flag
    if async_:
        drivername = "postgresql+asyncpg"
    else:
        # Use the standard synchronous driver. Assumes psycopg2 is installed.
        drivername = "postgresql+psycopg2"

        # Manually construct the URL object from individual, clean components.
    url = URL.create(
        drivername=drivername,
        username=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD.get_secret_value(),
        host=host,
        port=port,
        database=settings.DATABASE_NAME,
    )

    timeout_kwargs = {
        "pool_timeout": settings.DATABASE_ENGINE_POOL_TIMEOUT,
        "pool_recycle": settings.DATABASE_ENGINE_POOL_RECYCLE,
        "pool_size": settings.DATABASE_ENGINE_POOL_SIZE,
        "max_overflow": settings.DATABASE_ENGINE_MAX_OVERFLOW,
        "pool_pre_ping": settings.DATABASE_ENGINE_POOL_PING,
    }

    # Use the appropriate engine creation function
    if async_:
        return create_async_engine(url, **timeout_kwargs, echo=echo, connect_args=connect_args)
    else:
        return create_engine(url, **timeout_kwargs, echo=echo, connect_args=connect_args)

# Create the default asynchronous engine for your application
engine = create_db_engine(async_=True, echo=False)

# Create a synchronous engine, for example, for a script or a migration tool
# Note: You will need to have a synchronous driver like 'psycopg2-binary' installed.
engine_sync = create_db_engine(async_=False, echo=True)

# Enable query timing logging
#
# Set up logging for query debugging
#
#
# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     conn.info.setdefault("query_start_time", []).append(time.time())
#     logger.debug("Start Query: %s", statement)

# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     total = time.time() - conn.info["query_start_time"].pop(-1)
#     logger.debug("Query Complete!")
#     logger.debug("Total Time: %f", total)
#     # Log queries that take more than 1 second as warnings
#     if total > 1.0:
#         logger.warning("Slow Query (%.2fs): %s", total, statement)


SessionLocal = async_sessionmaker(bind=engine)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


raise_attribute_error = object()


def resolve_attr(obj, attr, default=None):
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


class ReprMixin:
    """Mixin providing __repr__, dict(), tablename, …"""

    __repr_attrs__: ClassVar[list[str]] = []
    __repr_max_length__: ClassVar[int] = 15

    # --- automatic __tablename__ ----------------------------------
    # @declared_attr.directive
    # def __tablename__(cls) -> str:  # type: ignore[override]
    #     return resolve_table_name(cls.__name__)

    # --- utility helpers ------------------------------------------
    def dict(self) -> dict[str, Any]:
        """Return a plain-dict view of column values."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore[attr-defined]

    # internal helpers extracted from your original code
    @property
    def _id_str(self) -> str:  # pragma: no cover
        ids = inspect(self).identity
        if ids:
            return "-".join(map(str, ids)) if len(ids) > 1 else str(ids[0])
        return "None"

    @property
    def _repr_attrs_str(self) -> str:  # pragma: no cover
        max_length = self.__repr_max_length__
        single = len(self.__repr_attrs__) == 1
        values = []
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(f"{self.__class__} has incorrect attribute '{key}' in __repr_attrs__")
            val = getattr(self, key)
            quoted = isinstance(val, str)
            val_str = str(val)[:max_length] + ("..." if len(str(val)) > max_length else "")
            if quoted:
                val_str = f"'{val_str}'"
            values.append(val_str if single else f"{key}:{val_str}")
        return " ".join(values)

    # nice printable representation
    def __repr__(self) -> str:  # pragma: no cover
        id_str = f"#{self._id_str}" if self._id_str else ""
        attrs = f" {self._repr_attrs_str}" if self._repr_attrs_str else ""
        return f"<{self.__class__.__name__} {id_str}{attrs}>"


class Base(ReprMixin, DeclarativeBase):
    """Project-wide declarative base (inherits mixin behaviour)."""


def get_db(request: Request) -> AsyncSession:
    """Get database session from request state."""
    session = request.state.db
    if not hasattr(session, "_farmbase_session_id"):
        session._farmbase_session_id = SessionTracker.track_session(session, context="fastapi_request")
    return session


DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name):
        for mapper in Base.registry.mappers:
            cls = mapper.class_
            if hasattr(cls, "__tablename__") and cls.__tablename__ == name:
                return cls
        return None

    # def _find_class(name):
    #     for c in Base._decl_class_registry.values():
    #         if hasattr(c, "__table__"):
    #             if c.__table__.fullname.lower() == name.lower():
    #                 return c

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    # try looking in the 'farmbase_core' schema
    if not mapped_class:
        mapped_class = _find_class(f"farmbase_core.{mapped_name}")

    if not mapped_class:
        raise ValidationError.from_exception_data(
            "BaseModel",
            [
                {
                    "loc": ("filterr",),
                    "msg": "Model not found. Check the name of your model.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return mapped_class


def get_table_name_by_class_instance(class_instance: Base) -> str:
    """Returns the name of the table for a given class instance."""
    return class_instance._sa_instance_state.mapper.mapped_table.name


def ensure_unique_default_per_project(target, value, oldvalue, initiator):
    """Ensures that only one row in table is specified as the default."""
    session = object_session(target)
    if session is None:
        return

    mapped_cls = get_mapper(target)

    if value:
        previous_default = (
            session.query(mapped_cls)
            .filter(mapped_cls.columns.default == true())
            .filter(mapped_cls.columns.project_id == target.project_id)
            .one_or_none()
        )
        if previous_default:
            # we want exclude updating the current default
            if previous_default.id != target.id:
                previous_default.default = False
                session.commit()


def refetch_db_session(organization_slug: str) -> Session:
    """Create a new database session for a specific organization."""
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"farmbase_organization_{organization_slug}",
        }
    )
    session = sessionmaker(bind=schema_engine)()
    session._farmbase_session_id = SessionTracker.track_session(session, context=f"organization_{organization_slug}")
    return session


async def get_schema_names(_engine: AsyncEngine) -> list[str]:
    def _get_schema_names(sync_conn):
        inspector = inspect(sync_conn)
        return inspector.get_schema_names()

    logger.info(_engine.url)
    async with _engine.connect() as async_conn:
        return await async_conn.run_sync(_get_schema_names)


class BaseFilterSet(AsyncFilterSet[Model]):
    limit_offset = LimitOffsetFilter()


#
# @contextmanager
# def get_session() -> Session:
#     """Context manager to ensure the session is closed after use."""
#     session = SessionLocal()
#     session_id = SessionTracker.track_session(session, context="context_manager")
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         SessionTracker.untrack_session(session_id)
#         session.close()
#
#
# @contextmanager
# def get_organization_session(organization_slug: str) -> Session:
#     """Context manager to ensure the organization session is closed after use."""
#     session = refetch_db_session(organization_slug)
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         if hasattr(session, "_farmbase_session_id"):
#             SessionTracker.untrack_session(session._farmbase_session_id)
#         session.close()

from configparser import RawConfigParser

from alembic import context
from farmbase.config import settings
from farmbase.database.core import Base
from loguru import logger
from sqlalchemy import engine_from_config, pool, text

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.


config.file_config = RawConfigParser()
config.set_main_option("sqlalchemy.url", str(settings.sqlalchemy_database_sync_uri))

target_metadata = Base.metadata  # noqa

CORE_SCHEMA_NAME = "farmbase_core"

IGNORE_TABLES: list[str] = ["spatial_ref_sys"]

# ❯ uv run --package farmbase python -m alembic -c apps/farmbase/src/farmbase/alembic.ini -n core revision -m "Initial migration" --autogenerate
# /Users/markns/workspace/farmwise/apps/farmbase/src/farmbase/database/revisions/core/env.py:68: SAWarning: Did not recognize type 'public.geometry' of column 'the_geom'
#   context.run_migrations()

# https://github.com/sqlalchemy/alembic/discussions/1282
# def include_object(
#     object: SchemaItem,
#     name: Optional[str],
#     type_: Literal[
#         "schema",
#         "table",
#         "column",
#         "index",
#         "unique_constraint",
#         "foreign_key_constraint",
#     ],
#     reflected: bool,
#     compare_to: Optional[SchemaItem]
# ) -> bool:
#     if type_ == 'table' and (name in IGNORE_TABLES or object.info.get("skip_autogenerate", False)):
#         return False
#     return True


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if object.schema == CORE_SCHEMA_NAME:
            return True
    else:
        return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # don't create empty revisions
    def process_revision_directives(context, revision, directives):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info("No changes found skipping revision creation.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    logger.info("Migrating farmbase core schema...")
    # migrate common tables
    with connectable.connect() as connection:
        connection.execute(text(f'set search_path to "{CORE_SCHEMA_NAME}"'))
        connection.dialect.default_schema_name = CORE_SCHEMA_NAME
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
            # literal_binds=True,
            # dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

        connection.commit()


if context.is_offline_mode():
    logger.info("Can't run migrations offline")
else:
    run_migrations_online()

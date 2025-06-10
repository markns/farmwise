from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import create_database, database_exists

from farmbase import config
from farmbase.commodity.models import Commodity
from farmbase.organization.models import Organization

from ..farm.activity.models import ActivityType
from ..farm.platform.models import Platform
from ..plugin.models import Plugin
from ..project.models import Project
from .core import Base, sessionmaker
from .enums import FARMBASE_ORGANIZATION_SCHEMA_PREFIX


def version_schema(script_location: str):
    """Applies alembic versioning to schema."""

    # add it to alembic table
    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_command.stamp(alembic_cfg, "head")


def get_core_tables():
    """Fetches tables that belong to the 'farmbase_core' schema."""
    core_tables = []
    for _, table in Base.metadata.tables.items():
        if table.schema == "farmbase_core":
            core_tables.append(table)
    return core_tables


def get_tenant_tables():
    """Fetches tables that belong to their own tenant tables."""
    tenant_tables = []
    for _, table in Base.metadata.tables.items():
        if not table.schema:
            tenant_tables.append(table)
    return tenant_tables


def populate_static_data(session):
    # Check and add Platforms
    if not session.query(Platform).first():
        print("Populating static Platform data...")
        platforms_to_add = [
            Platform(platform_name="Web"),
            Platform(platform_name="Mobile App (iOS)"),
            Platform(platform_name="Mobile App (Android)"),
            Platform(platform_name="Machine Data Import"),
            Platform(platform_name="API Integration"),
        ]
        session.add_all(platforms_to_add)
        session.commit()
        print(f"{len(platforms_to_add)} Platforms added.")
    else:
        print("Platform data already exists.")

    # Check and add ActivityTypes
    if not session.query(ActivityType).first():
        print("Populating static ActivityType data...")
        activity_types_to_add = [
            ActivityType(activity_type_name="Planting", description="Recording crop planting activities."),
            ActivityType(activity_type_name="Fertilizing", description="Application of fertilizers."),
            ActivityType(
                activity_type_name="Spraying", description="Application of pesticides, herbicides, or fungicides."
            ),
            ActivityType(activity_type_name="Tillage", description="Soil cultivation activities."),
            ActivityType(activity_type_name="Irrigation", description="Water application activities."),
            ActivityType(activity_type_name="Harvesting", description="Crop harvesting activities."),
            ActivityType(activity_type_name="Scouting", description="Field scouting and observation."),
            ActivityType(activity_type_name="Soil Sampling", description="Collecting soil samples for analysis."),
            ActivityType(activity_type_name="Maintenance", description="Equipment or infrastructure maintenance."),
        ]
        session.add_all(activity_types_to_add)
        session.commit()
        print(f"{len(activity_types_to_add)} ActivityTypes added.")
    else:
        print("ActivityType data already exists.")

    # Verify data
    print("\n--- Verification ---")
    print(f"Total Platforms: {session.query(Platform).count()}")
    for p in session.query(Platform).all():
        print(f"  {p}")
    print(f"Total ActivityTypes: {session.query(ActivityType).count()}")
    for at in session.query(ActivityType).all():
        print(f"  {at}")
    print(f"Total Commodities: {session.query(Commodity).count()}")
    for c in session.query(Commodity).all():
        print(f"  {c}")


def init_database(engine):
    """Initializes the database."""
    if not database_exists(str(config.SQLALCHEMY_DATABASE_SYNC_URI)):
        print(f"Creating database {config.SQLALCHEMY_DATABASE_SYNC_URI}...")
        create_database(str(config.SQLALCHEMY_DATABASE_SYNC_URI))

    schema_name = "farmbase_core"

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

        inspector = inspect(conn)
        if schema_name not in inspector.get_schema_names():
            print(f"Creating schema {schema_name}...")
            conn.execute(CreateSchema(schema_name))

    tables = get_core_tables()

    Base.metadata.create_all(engine, tables=tables)

    version_schema(script_location=config.ALEMBIC_CORE_REVISION_PATH)
    # setup_fulltext_search(engine, tables)

    # setup an required database functions
    session = sessionmaker(bind=engine)
    db_session = session()

    # we create the default organization if it doesn't exist
    organization = db_session.query(Organization).filter(Organization.name == "default").one_or_none()

    if not organization:
        print("Creating default organization...")
        organization = Organization(
            name="default",
            slug="default",
            default=True,
            description="Default Farmbase organization.",
        )

        db_session.add(organization)
        db_session.commit()

    # we initialize the database schema
    init_schema(engine=engine, organization=organization)

    # we install all plugins
    from farmbase.common.utils.cli import install_plugins
    from farmbase.plugins.base import plugins

    install_plugins()

    for p in plugins.all():
        plugin = Plugin(
            title=p.title,
            slug=p.slug,
            type=p.type,
            version=p.version,
            author=p.author,
            author_url=p.author_url,
            multiple=p.multiple,
            description=p.description,
        )
        db_session.add(plugin)
    db_session.commit()

    # we create the default project if it doesn't exist
    project = db_session.query(Project).filter(Project.name == "default").one_or_none()
    if not project:
        print("Creating default project...")
        project = Project(
            name="default",
            default=True,
            description="Default Farmbase project.",
            organization=organization,
        )
        db_session.add(project)
        db_session.commit()

        # we initialize the project with defaults
        from farmbase.project import flows as project_flows

        print("Initializing default project...")
        project_flows.project_init_flow(
            project_id=project.id, organization_slug=organization.slug, db_session=db_session
        )

    populate_static_data(db_session)


def init_schema(*, engine, organization: Organization):
    """Initializes a new schema."""
    schema_name = f"{FARMBASE_ORGANIZATION_SCHEMA_PREFIX}_{organization.slug}"

    with engine.begin() as conn:
        inspector = inspect(conn)
        if schema_name not in inspector.get_schema_names():
            conn.execute(CreateSchema(schema_name))

    # set the schema for table creation
    tables = get_tenant_tables()

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: schema_name,
        }
    )

    Base.metadata.create_all(schema_engine, tables=tables)

    # put schema under version control
    version_schema(script_location=config.ALEMBIC_TENANT_REVISION_PATH)

    # with engine.connect() as connection:
    #     # we need to map this for full text search as it uses sql literal strings
    #     # and schema translate map does not apply
    #     for t in tables:
    #         t.schema = schema_name
    #
    #     setup_fulltext_search(connection, tables)

    for t in tables:
        t.schema = schema_name

    session = sessionmaker(bind=schema_engine)
    db_session = session()

    organization = db_session.merge(organization)
    db_session.add(organization)
    db_session.commit()
    return organization


# def setup_fulltext_search(connection, tables):
#     """Syncs any required fulltext table triggers and functions."""
#     # parsing functions
#     function_path = os.path.join(
#         os.path.dirname(os.path.abspath(fulltext.__file__)), "expressions.sql"
#     )
#     connection.execute(text(open(function_path).read()))
#
#     for table in tables:
#         table_triggers = []
#         for column in table.columns:
#             if column.name.endswith("search_vector"):
#                 if hasattr(column.type, "columns"):
#                     table_triggers.append(
#                         {
#                             "conn": connection,
#                             "table": table,
#                             "tsvector_column": "search_vector",
#                             "indexed_columns": column.type.columns,
#                         }
#                     )
#                 else:
#                     logger.warning(
#                         f"Column search_vector defined but no index columns found. Table: {table.name}"
#                     )
#
#         for trigger in table_triggers:
#             sync_trigger(**trigger)

import importlib
import os
import pkgutil

import click

from farmbase import __version__
from farmbase.config import settings
from farmbase.exceptions.exceptions import FarmBaseApiError

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@click.group()
@click.version_option(version=__version__)
def farmbase_cli():
    """Command-line interface to Farmbase."""
    ...


@farmbase_cli.group("plugins")
def plugins_group():
    """All commands for plugin manipulation."""
    pass


@plugins_group.command("list")
def list_plugins():
    """Shows all available plugins."""
    from tabulate import tabulate

    from farmbase.database.core import SessionLocal
    from farmbase.plugin import service as plugin_service

    db_session = SessionLocal()
    table = []
    for record in plugin_service.get_all(db_session=db_session):
        table.append(
            [
                record.title,
                record.slug,
                record.version,
                record.type,
                record.author,
                record.description,
            ]
        )

    click.secho(
        tabulate(
            table,
            headers=[
                "Title",
                "Slug",
                "Version",
                "Type",
                "Author",
                "Description",
            ],
        ),
        fg="blue",
    )


@plugins_group.command("install")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force a plugin to update all details about itself, this will overwrite the current database entry.",
)
def install_plugins(force):
    """Installs all plugins, or only one."""
    from farmbase.common.utils.cli import install_plugins
    from farmbase.database.core import SessionLocal
    from farmbase.plugin import service as plugin_service
    from farmbase.plugin.models import Plugin, PluginEvent
    from farmbase.plugins.base import plugins

    install_plugins()

    db_session = SessionLocal()
    for p in plugins.all():
        record = plugin_service.get_by_slug(db_session=db_session, slug=p.slug)
        if not record:
            click.secho(f"Installing plugin... Slug: {p.slug} Version: {p.version}", fg="blue")
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
            record = plugin
        else:
            if force:
                click.secho(f"Updating plugin... Slug: {p.slug} Version: {p.version}", fg="blue")
                # we only update values that should change
                record.title = p.title
                record.version = p.version
                record.author = p.author
                record.author_url = p.author_url
                record.description = p.description
                record.type = p.type

        # Registers the plugin events with the plugin or updates the plugin events
        for plugin_event_in in p.plugin_events:
            click.secho(f"  Registering plugin event... Slug: {plugin_event_in.slug}", fg="blue")
            if plugin_event := plugin_service.get_plugin_event_by_slug(
                    db_session=db_session, slug=plugin_event_in.slug
            ):
                plugin_event.name = plugin_event_in.name
                plugin_event.description = plugin_event_in.description
                plugin_event.plugin = record
            else:
                plugin_event = PluginEvent(
                    name=plugin_event_in.name,
                    slug=plugin_event_in.slug,
                    description=plugin_event_in.description,
                    plugin=record,
                )
                db_session.add(plugin_event)
        db_session.commit()


@plugins_group.command("uninstall")
@click.argument("plugins", nargs=-1)
def uninstall_plugins(plugins):
    """Uninstalls all plugins, or only one."""
    from farmbase.database.core import SessionLocal
    from farmbase.plugin import service as plugin_service

    db_session = SessionLocal()

    for plugin_slug in plugins:
        plugin = plugin_service.get_by_slug(db_session=db_session, slug=plugin_slug)
        if not plugin:
            click.secho(
                f"Plugin slug {plugin_slug} does not exist. Make sure you're passing the plugin's slug.",
                fg="red",
            )

        plugin_service.delete(db_session=db_session, plugin_id=plugin.id)


@farmbase_cli.group("database")
def farmbase_database():
    """Container for all farmbase database commands."""
    pass


@farmbase_database.command("init")
def database_init():
    """Initializes a new database."""
    click.echo("Initializing new database...")
    from .database.core import engine_sync as engine
    from .database.manage import init_database

    init_database(engine)
    click.secho("Success.", fg="green")


# @farmbase_database.command("restore")
# @click.option(
#     "--dump-file",
#     default="farmbase-backup.dump",
#     help="Path to a PostgreSQL text format dump file.",
# )
# def restore_database(dump_file):
#     """Restores the database via psql."""
#     from sh import ErrorReturnCode_1, createdb, psql
#
#     from farmbase.config import (
#         DATABASE_CREDENTIALS,
#         DATABASE_HOSTNAME,
#         DATABASE_NAME,
#         DATABASE_PORT,
#     )
#
#     username, password = str(DATABASE_CREDENTIALS).split(":")
#
#     try:
#         print(
#             createdb(
#                 "-h",
#                 DATABASE_HOSTNAME,
#                 "-p",
#                 DATABASE_PORT,
#                 "-U",
#                 username,
#                 DATABASE_NAME,
#                 _env={"PGPASSWORD": password},
#             )
#         )
#     except ErrorReturnCode_1:
#         print("Database already exists.")
#
#     print(
#         psql(
#             "-h",
#             DATABASE_HOSTNAME,
#             "-p",
#             DATABASE_PORT,
#             "-U",
#             username,
#             "-d",
#             DATABASE_NAME,
#             "-f",
#             dump_file,
#             _env={"PGPASSWORD": password},
#         )
#     )
#     click.secho("Success.", fg="green")


# @farmbase_database.command("dump")
# @click.option(
#     "--dump-file",
#     default="farmbase-backup.dump",
#     help="Path to a PostgreSQL text format dump file.",
# )
# def dump_database(dump_file):
#     """Dumps the database via pg_dump."""
#     from sh import pg_dump
#
#     from farmbase.config import (
#         DATABASE_CREDENTIALS,
#         DATABASE_HOSTNAME,
#         DATABASE_NAME,
#         DATABASE_PORT,
#     )
#
#     username, password = str(DATABASE_CREDENTIALS).split(":")
#
#     pg_dump(
#         "-f",
#         dump_file,
#         "-h",
#         DATABASE_HOSTNAME,
#         "-p",
#         DATABASE_PORT,
#         "-U",
#         username,
#         DATABASE_NAME,
#         _env={"PGPASSWORD": password},
#     )


@farmbase_database.command("drop")
def drop_database():
    """Drops all data in database."""
    from sqlalchemy_utils import database_exists, drop_database

    sqlalchemy_database_uri = str(settings.sqlalchemy_database_sync_uri)

    if database_exists(str(sqlalchemy_database_uri)):
        if click.confirm(f"Are you sure you want to drop database? {str(sqlalchemy_database_uri)}"):
            drop_database(str(sqlalchemy_database_uri))
            click.secho("Success.", fg="green")
    else:
        click.secho(f"Database '{sqlalchemy_database_uri}' does not exist!!!", fg="red")


@farmbase_database.command("upgrade")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
def upgrade_database(tag, sql, revision, revision_type):
    """Upgrades database schema to the newest version."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig
    from sqlalchemy_utils import database_exists

    from .database.core import engine_sync as engine
    from .database.manage import init_database

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)

    # importlib.import_module(".contact.models.Contact")
    if not database_exists(str(settings.sqlalchemy_database_sync_uri)):
        click.secho("Found no database to upgrade, initializing new database...")
        init_database(engine)
    else:
        if revision_type:
            if revision_type == "core":
                path = settings.ALEMBIC_CORE_REVISION_PATH

            elif revision_type == "tenant":
                path = settings.ALEMBIC_TENANT_REVISION_PATH

            alembic_cfg.set_main_option("script_location", path)
            alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)
        else:
            for path in [settings.ALEMBIC_CORE_REVISION_PATH, settings.ALEMBIC_TENANT_REVISION_PATH]:
                alembic_cfg.set_main_option("script_location", path)
                alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)

    click.secho("Success.", fg="green")


@farmbase_database.command("merge")
@click.argument("revisions", nargs=-1)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option("--message")
def merge_revisions(revisions, revision_type, message):
    """Combines two revisions."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = settings.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = settings.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.merge(alembic_cfg, revisions, message=message)


@farmbase_database.command("heads")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def head_database(revision_type):
    """Shows the heads of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = settings.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = settings.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.heads(alembic_cfg)


@farmbase_database.command("history")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def history_database(revision_type):
    """Shows the history of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = settings.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = settings.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.history(alembic_cfg)


@farmbase_database.command("downgrade")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def downgrade_database(tag, sql, revision, revision_type):
    """Downgrades database schema to next newest version."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    if sql and revision == "-1":
        revision = "head:-1"

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = settings.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = settings.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.downgrade(alembic_cfg, revision, sql=sql, tag=tag)
    click.secho("Success.", fg="green")


@farmbase_database.command("stamp")
@click.argument("revision", nargs=1, default="head")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option("--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts.")
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
def stamp_database(revision, revision_type, tag, sql):
    """Forces the database to a given revision."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)

    if revision_type == "core":
        path = settings.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = settings.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.stamp(alembic_cfg, revision, sql=sql, tag=tag)


@farmbase_database.command("revision")
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=("Populate revision script with candidate migration operations, based on comparison of database to model"),
)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
@click.option("--sql", is_flag=True, help=("Don't emit SQL to database - dump to standard output instead"))
@click.option(
    "--head",
    default="head",
    help=("Specify head revision or <branchname>@head to base new revision on"),
)
@click.option("--splice", is_flag=True, help=('Allow a non-head revision as the "head" to splice onto'))
@click.option("--branch-label", default=None, help=("Specify a branch label to apply to the new revision"))
@click.option("--version-path", default=None, help=("Specify specific path from config for version file"))
@click.option("--rev-id", default=None, help=("Specify a hardcoded revision id instead of generating one"))
def revision_database(message, autogenerate, revision_type, sql, head, splice, branch_label, version_path, rev_id):
    """Create new database revision."""
    import types

    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(settings.ALEMBIC_INI_PATH)

    if revision_type:
        if revision_type == "core":
            path = settings.ALEMBIC_CORE_REVISION_PATH
        elif revision_type == "tenant":
            path = settings.ALEMBIC_TENANT_REVISION_PATH

        alembic_cfg.set_main_option("script_location", path)
        alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
        alembic_command.revision(
            alembic_cfg,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id,
        )
    else:
        for path in [
            settings.ALEMBIC_CORE_REVISION_PATH,
            settings.ALEMBIC_TENANT_REVISION_PATH,
        ]:
            alembic_cfg.set_main_option("script_location", path)
            alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
            alembic_command.revision(
                alembic_cfg,
                message,
                autogenerate=autogenerate,
                sql=sql,
                head=head,
                splice=splice,
                branch_label=branch_label,
                version_path=version_path,
                rev_id=rev_id,
            )


@farmbase_cli.group("server")
def farmbase_server():
    """Container for all farmbase server commands."""
    pass


@farmbase_server.command("routes")
def show_routes():
    """Prints all available routes."""
    from tabulate import tabulate

    from farmbase.main import api_router

    table = []
    for r in api_router.routes:
        table.append([r.path, ",".join(r.methods)])

    click.secho(tabulate(table, headers=["Path", "Authenticated", "Methods"]), fg="blue")


@farmbase_server.command("config")
def show_config():
    """Prints the current config as farmbase sees it."""

    from tabulate import tabulate

    table = []
    for key, value in settings.model_dump().items():
        if key.isupper():
            table.append([key, value])

    click.secho(tabulate(table, headers=["Key", "Value"]), fg="blue")


@farmbase_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    """Starts an ipython shell importing our app. Useful for debugging."""
    import sys

    import IPython
    from IPython.terminal.ipapp import load_default_config

    config = load_default_config()

    config.TerminalInteractiveShell.banner1 = f"""Python {sys.version} on {sys.platform}
IPython: {IPython.__version__}"""

    IPython.start_ipython(argv=ipython_args, user_ns={}, config=config)


def entrypoint():
    """The entry that the CLI is executed from"""

    try:
        farmbase_cli()
    except FarmBaseApiError as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()

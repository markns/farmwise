import logging

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)


def configure_extensions():
    logger.debug("Configuring extensions...")
    # if SENTRY_DSN:
    #     sentry_sdk.init(
    #         dsn=str(SENTRY_DSN),
    #         integrations=[
    #             AioHttpIntegration(),
    #             AtexitIntegration(),
    #             DedupeIntegration(),
    #             ExcepthookIntegration(),
    #             ModulesIntegration(),
    #             SqlalchemyIntegration(),
    #             StdlibIntegration(),
    #             sentry_logging,
    #         ],
    #         environment=ENV,
    #         auto_enabling_integrations=False,
    #     )
    #     with sentry_sdk.configure_scope() as scope:
    #         logger.debug(f"Using the following tags... ENV_TAGS: {ENV_TAGS}")
    #         for k, v in ENV_TAGS.items():
    #             scope.set_tag(k, v)

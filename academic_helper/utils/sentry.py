import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from academic_helper.utils.environment import ENV, Environment

DSN = os.getenv("SENTRY_DSN", None)


def init_sentry():
    from academic_helper.utils.logger import log

    if ENV == Environment.local:
        log.info("Env set to local, not configuring sentry")
        return
    if not DSN:
        log.info("Sentry DSN env var not found")
        return
    log.info("Configuring Sentry")
    integrations = [DjangoIntegration()]
    if ENV != Environment.prod:
        integrations += [LoggingIntegration(event_level=None)]
    sentry_sdk.init(
        dsn=DSN, integrations=integrations, environment=ENV.value, send_default_pii=True,
    )
    sentry_sdk.integrations.logging.ignore_logger("django.security.DisallowedHost")

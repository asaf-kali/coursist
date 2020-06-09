import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from academic_helper.utils.environment import ENV

DSN = os.getenv("SENTRY_DSN", None)


def init_sentry():
    from academic_helper.utils.logger import log

    if not DSN:
        log.info("Sentry DSN env var not found")
        return
    log.info("Configuring Sentry")
    sentry_sdk.init(dsn=DSN, integrations=[DjangoIntegration()], environment=ENV.value, send_default_pii=True)

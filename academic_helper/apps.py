from django.apps import AppConfig

from academic_helper.utils.sentry import init_sentry


class AcademicHelperConfig(AppConfig):
    name = "academic_helper"
    verbose_name = "Academic Helper"

    def ready(self):
        init_sentry()

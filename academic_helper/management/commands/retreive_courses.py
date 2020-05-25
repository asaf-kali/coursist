from django.core.management import BaseCommand

from academic_helper.utils.logger import log


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Hi")

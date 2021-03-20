import logging

from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("course_number", type=int)

    def handle(self, *args, **options) -> str:
        course_number = options["course_number"]
        log.info(f"Fetching course_number = {course_number}")
        parser = ShnatonParser()
        return str(parser.fetch_course(course_number).id)

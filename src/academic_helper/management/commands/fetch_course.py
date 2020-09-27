from django.core.management import BaseCommand

from academic_helper.logic import ShnatonParser


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("course_number", type=int)

    def handle(self, *args, **options):
        course_number = options["course_number"]
        print(f"fetching course_number = {course_number}")
        parser = ShnatonParser()
        parser.fetch_course(course_number)

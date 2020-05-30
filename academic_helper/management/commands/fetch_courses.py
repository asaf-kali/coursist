import json

from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser


# TODO: Add arguments: src file, limit
class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("courses_2020") as file:
            courses = json.load(file)
        for i, course in enumerate(courses):
            if i > 20:
                break
            ShnatonParser.fetch_course(course["id"])

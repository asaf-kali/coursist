import json

from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser
# TODO: Add arguments: src file, limit
from academic_helper.utils.logger import log


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("courses_2020.json", encoding="utf8") as file:
            courses = json.load(file)
        fail_count = 0
        for i, course in enumerate(courses):
            if i > 20:
                break
            course_id = course["id"]
            try:
                ShnatonParser.fetch_course(course_id)
            except Exception as e:
                log.error(f"Could'nt fetch course {course_id}: {e}")
                fail_count += 1
        print(f"Fail count:", fail_count)

import json
import traceback

from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser

# TODO: Add arguments: src file, limit
from academic_helper.models import Course
from academic_helper.utils.logger import log

LIMIT = 100
SKIP_EXISTING = True


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("courses_2020.json", encoding="utf8") as file:
            courses = json.load(file)
        fail_count = 0
        for i, course in enumerate(courses):
            # if i > 100:
            #     break
            course_number = course["id"]
            if SKIP_EXISTING:
                if Course.objects.filter(course_number=course_number).exists():
                    continue
            try:
                ShnatonParser.fetch_course(course_number)
            except Exception as e:
                log.error(f"Could'nt fetch course {course_number}: {e}")
                fail_count += 1
        print(f"Fail count:", fail_count)

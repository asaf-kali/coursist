import json
import random

from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import Course
from academic_helper.utils.logger import log, wrap

DEFAULT_SRC_FILE = "courses_2020.json"

DEFAULT_LIMIT = 50
SHUFFLE = True


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--src_file",
            type=str,
            default=DEFAULT_SRC_FILE,
            help=f"Source file for courses (Default is {DEFAULT_SRC_FILE}).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_LIMIT,
            help=f"Max number of courses to fetch (Default is {DEFAULT_LIMIT}).",
        )
        parser.add_argument(
            "--fetch_existing",
            default=False,
            action="store_true",
            help="Fetch existing courses (default is False). If set to True, existing courses will be deleted!",
        )

    def handle(self, *args, **options):
        with open(options["src_file"], encoding="utf8") as file:
            courses = json.load(file)
        if SHUFFLE:
            random.shuffle(courses)
        fail_count = 0
        log.info(f"Total {wrap(len(courses))} courses found")
        for i, course in enumerate(courses):
            if i > options["limit"]:
                break
            course_number = course["id"]
            existing = Course.objects.filter(course_number=course_number)
            if existing.exists():
                if not options["fetch_existing"]:
                    continue
                existing.delete()
            try:
                ShnatonParser.fetch_course(course_number)
            except Exception as e:
                log.error(f"Could'nt fetch course {course_number}: {e}")
                fail_count += 1
        log.info(f"Fail count: {wrap(fail_count)}")

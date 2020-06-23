from django.core.management import BaseCommand

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import Course, StudyBlock, StudyPlan, CoursistUser
from academic_helper.utils.logger import log

courses_to_fetch = [94640, 94625, 67504, 67101, 67392, 67829]  # Intro  # Crypto  # Impr


def create_admin():
    admin, created = CoursistUser.objects.get_or_create(
        username="admin",
        first_name="Local",
        last_name="Adminovski",
        is_superuser=True,
        is_staff=True,
        email="admin@coursist.xyz",
    )
    admin.set_password("123456")
    admin.save()


def fetch_courses():
    log.info("Fetching courses")
    for course_number in courses_to_fetch:
        ShnatonParser.fetch_course(course_number)


def create_blocks():
    log.info("Creating blocks")
    intro = Course.objects.get(course_number=67101)
    crypto = Course.objects.get(course_number=67392)
    impr = Course.objects.get(course_number=67829)
    must_cs_block = StudyBlock.objects.get_or_create(name="Must CS", min_credits=32)[0]
    must_cs_block.courses.add(intro)
    must_cs_block.save()
    cs_elective_block = StudyBlock.objects.get_or_create(name="CS Must Elective", min_credits=16)[0]
    cs_elective_block.courses.add(crypto)
    cs_elective_block.courses.add(impr)
    cs_elective_block.save()
    return cs_elective_block, must_cs_block


def create_study_plans(cs_elective_block, must_cs_block):
    log.info("Creating plans")
    cs_plan = StudyPlan.objects.get_or_create(name="CS Expanded Single Major", credits=134)[0]
    cs_plan.blocks.add(must_cs_block)
    cs_plan.blocks.add(cs_elective_block)
    cs_plan.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_courses()
        cs_elective_block, must_cs_block = create_blocks()
        create_study_plans(cs_elective_block, must_cs_block)

from django.core.management import BaseCommand

from academic_helper.models import Course, StudyBlock, StudyPlan
from academic_helper.utils.logger import log


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Creating courses")
        intro = Course.objects.get_or_create(course_number=67101, name="Intro To Cs", credits=7)[0]
        crypto = Course.objects.get_or_create(
            course_number=67392, name="Introduction To Cryptography And Software Security", credits=4
        )[0]
        impr = Course.objects.get_or_create(course_number=67829, name="Image Processing", credits=4)[0]

        log.info("Creating blocks")
        must_cs_block = StudyBlock.objects.get_or_create(name="Must CS", min_credits=32)[0]
        must_cs_block.courses.add(intro)
        must_cs_block.save()
        cs_elective_block = StudyBlock.objects.get_or_create(name="CS Must Elective", min_credits=16)[0]
        cs_elective_block.courses.add(crypto)
        cs_elective_block.courses.add(impr)
        cs_elective_block.save()

        log.info("Creating plans")
        cs_plan = StudyPlan.objects.get_or_create(name="CS Expanded Single Major", credits=134)[0]
        cs_plan.blocks.add(must_cs_block)
        cs_plan.blocks.add(cs_elective_block)
        cs_plan.save()

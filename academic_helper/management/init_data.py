from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import Course, StudyBlock, DegreeProgram, CoursistUser, University
from academic_helper.utils.logger import log

COURSES_TO_FETCH = [94640, 94625, 67504, 67101, 67392, 67829]

# blocks info - name, min_credits, [course_num1, ...]
UNPARSED_BLOCKS = [
    ("חובה - מדעי המחשב", 56, [67101, 67109, 67125, 67808]),
    ("חובה - מתמטיקה", 32, [80131, 80133, 80134, 80430]),
    ("חובת בחירה", 16, [67392, 67829, 67506, 67609, 67392]),
    ("בחירה בחוג", 16, [67625, 67118, 67609, 67629]),
    ("אבני פינה", 8, [72159, 23331]),
    ("לימודים משלימים", 6, [55904,]),
]


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


def create_james():
    james, created = CoursistUser.objects.get_or_create(
        username="james", first_name="James", last_name="Johnson", email="james@coursist.xyz",
    )
    james.set_password("123456")
    james.save()


def fetch_courses():
    University.objects.get_or_create(
        abbreviation="HUJI", name="האוניברסיטה העברית", english_name="The Hebrew University of Jerusalem"
    )
    log.info("Fetching courses")
    parser = ShnatonParser()
    for course_number in COURSES_TO_FETCH:
        parser.fetch_course(course_number)
    for block in UNPARSED_BLOCKS:
        for course in block[2]:
            try:
                parser.fetch_course(course)
            except Exception as e:
                log.error(e)


def create_blocks():
    log.info("Creating blocks")
    study_blocks = []
    for unparsed_block in UNPARSED_BLOCKS:
        # extract info
        name, min_credits, course_nums = unparsed_block
        # create block
        block = StudyBlock.objects.get_or_create(name=name, min_credits=min_credits)[0]
        # add courses to block
        for course_num in course_nums:
            course = Course.objects.get(course_number=course_num)
            block.courses.add(course)
        # add block to study blocks
        block.save()
        study_blocks.append(block)
    return study_blocks


def create_degree_program(blocks):
    log.info("Creating program")
    cs_plan = DegreeProgram.objects.get_or_create(name="מדעי המחשב מורחב", code=3010, credits=134)[0]
    for block in blocks:
        cs_plan.blocks.add(block)
    cs_plan.save()


def create_all():
    create_admin()
    create_james()
    fetch_courses()
    blocks = create_blocks()
    create_degree_program(blocks)

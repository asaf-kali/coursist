import os
import re
import urllib
from os import path
from typing import Optional, List, Tuple
from urllib import request
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.db.transaction import atomic

from academic_helper.models import Course, School, Faculty
from academic_helper.models.course_occurrence import (
    CourseOccurrence,
    Semester,
    ClassGroup,
    ClassType,
    CourseClass,
    DayOfWeek,
    Hall,
    Campus,
    Teacher,
)
from academic_helper.utils.logger import log

SHNATON_URL = "https://shnaton.huji.ac.il/index.php"
CHARSET = "windows-1255"


def parse_course_semester(semester: str) -> List[Semester]:
    if semester == "סמסטר א' או/ו ב'":
        return [Semester.A, Semester.B]
    elif semester == "סמסטר א'":
        return [Semester.A]
    elif semester == "סמסטר ב'":
        return [Semester.B]
    elif semester == "קיץ" or semester == "סמסטר קיץ":
        return [Semester.SUMMER]
    elif semester == "שנתי":
        return [Semester.YEARLY]
    raise NotImplementedError(f"Unrecognized course semester: {semester}")


def parse_lesson_semester(semester: str) -> Semester:
    if semester == "סמסטר א" or semester == "סמסטר א'":
        return Semester.A
    elif semester == "סמסטר ב" or semester == "סמסטר ב'":
        return Semester.B
    elif semester == "קיץ" or semester == "סמסטר קיץ":
        return Semester.SUMMER
    elif semester == "שנתי":
        return Semester.YEARLY
    raise NotImplementedError(f"Unrecognized lesson semester: {semester}")


def parse_group_semester(semesters: List[str]) -> Semester:
    semesters = {parse_lesson_semester(semester) for semester in semesters}
    if len(semesters) == 1:
        return semesters.pop()
    elif Semester.A in semesters and Semester.B in semesters:
        return Semester.YEARLY
    elif Semester.YEARLY in semesters:
        return Semester.YEARLY
    raise ValueError(f"Can't find common semester for {semesters}")


def parse_group_type(class_type: str) -> ClassType:
    if class_type == "שעור":
        return ClassType.LECTURE
    if class_type == "תרג":
        return ClassType.RECITATION
    if class_type == "סמ":
        return ClassType.SEMINAR
    if class_type == "מעב":
        return ClassType.LAB
    if class_type == "סדנה":
        return ClassType.WORKSHOP
    if class_type == "מטלה":
        return ClassType.ASSIGNMENT
    if class_type == "שק":
        return ClassType.CLINICAL
    if class_type == "סיור":
        return ClassType.TRIP
    if class_type == "מכי":
        return ClassType.PREPARATORY
    if class_type == "הדר":
        return ClassType.GUIDANCE
    if class_type == "שומ":
        return ClassType.LESSON_AND_LAB
    if class_type == "שות":
        return ClassType.SHUT
    if class_type == "ע.מע":
        return ClassType.PRACTICAL_WORK
    if class_type == "שוסד":
        return ClassType.LESSON_AND_WORKSHOP
    if class_type == "שוה":
        return ClassType.LESSON_AND_GUIDANCE
    if class_type == "שוס":
        return ClassType.LESSON_AND_SEMINAR
    if class_type == "מחנה":
        return ClassType.CAMP
    raise NotImplementedError(f"Unrecognized class type: {class_type}")


def parse_day_of_week(day: str) -> DayOfWeek:
    if day == "יום א'":
        return DayOfWeek.SUNDAY
    if day == "יום ב'":
        return DayOfWeek.MONDAY
    if day == "יום ג'":
        return DayOfWeek.TUESDAY
    if day == "יום ד'":
        return DayOfWeek.WEDNESDAY
    if day == "יום ה'":
        return DayOfWeek.THURSDAY
    if day == "יום ו'":
        return DayOfWeek.FRIDAY
    raise NotImplementedError(f"Unrecognized day of week: {day}")


def parse_times(times: str) -> Tuple[str, str]:
    result = re.match(r"([\d]{2}:[\d]{2})-([\d]{2}:[\d]{2})", times)
    return result[2], result[1]


def parse_hall(raw_hall: str) -> Hall:
    match = re.match(r"(.*) \((.*)\)", raw_hall)
    if match:
        campus = Campus.objects.get_or_create(name=match[2])[0]
        hall = Hall.objects.get_or_create(name=match[1], campus=campus)[0]
    else:
        hall = Hall.objects.get_or_create(name=raw_hall)[0]
    return hall


def expand_teacher_list(teachers: List[str], length: int) -> List[str]:
    if len(teachers) == length or len(teachers) > length:
        return teachers
    while len(teachers) < length:
        # TODO: Make sure this is reached only when needed
        teachers.append(teachers[-1])
    return teachers


def parse_course_credits(year, raw_data):
    occurrence_year = raw_data["year"]
    assert str(occurrence_year) == str(year)
    occurrence_credits = raw_data["nz"]
    return occurrence_credits


def parse_teacher(teacher: str) -> Teacher:
    return Teacher.objects.get_or_create(name=teacher)[0]


def parse_hours(hours):
    ret = list()

    for hour in hours.contents:
        if hour.string is not None:
            # not <br>, append it
            ret.append(hour.string)

    return ret


def parse_days(days):
    ret = list()

    for day in days.contents:
        if day.string is not None:
            # not <br>, append it
            ret.append(day.string)

    return ret


def parse_semester(semesters):
    ret = list()

    for semester in semesters.contents:
        if semester.string is not None:
            # not <br>, append it
            ret.append(semester.string)

    return ret


def parse_halls(halls):
    ret = list()
    hall_children = halls.find_all("b")
    if not hall_children:
        # This is patch for 1921 and likewise
        hall_children = halls.contents
    for hall in hall_children:
        if hall.string is not None:
            ret.append(hall.string.replace("\n", ""))

    return ret


def parse_lecturers(lecturers):
    ret = list()

    for lecturer in lecturers.contents:
        # TODO: This order is not right for course 1921!
        if lecturer.string is not None:
            ret.append(lecturer.string)
        elif lecturer.name == "br" and lecturer.previous_sibling not in ret:
            ret.append(ret[-1])

    return ret


LESSON_TABLE_CELL_NUM = 8  # number of <td>s in the lesson table rows


class ShnatonParser:

    def __init__(self, shnaton_url: str = SHNATON_URL, cache_dir: str = None, use_cache: bool = True):
        self.shnaton_url = shnaton_url
        if not cache_dir:
            cache_dir = path.join("academic_helper", "shnaton_cache")
        self.cache_dir = cache_dir
        if not path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.use_cache = use_cache

    @atomic
    def fetch_course(self, course_number: int, year: int = 2020) -> Optional[Course]:
        """
        Fetch course from Shnaton, add it to the database and return it.
        :param course_number: The course number to search.
        :param year: The year to look for in the shnaton.
        :return: The course model object of the fetched course and its classes,
         or None if the course wasn't found.
        """
        if not isinstance(course_number, int):
            course_number = int(course_number)

        raw_data = self.extract_data_from_shnaton(year, course_number)
        if raw_data is None:
            return None

        raw_faculty = raw_data["faculty"].strip(" :\t")
        raw_school = raw_data["school"].strip(" :\t")
        faculty = Faculty.objects.get_or_create(name=raw_faculty)[0]
        school = School.objects.get_or_create(name=raw_school, faculty=faculty)[0]

        course_number = raw_data["id"]
        course_name = raw_data["name"].replace("_", "")
        # if "name_en" in raw_data and len(raw_data["name_en"].replace(" ", "")) > 5:
        #     course_name = raw_data["name_en"]
        course = Course.objects.get_or_create(name=course_name, course_number=course_number, school=school)[0]

        course_semesters = parse_course_semester(raw_data["semester"])
        occurrence_credits = parse_course_credits(year, raw_data)

        for raw_group in raw_data["lessons"]:
            self.create_course_groups(course, year, course_semesters, occurrence_credits, raw_group)
        return course

    def occurrence_for_semester(
        self, course: Course, year: int, occurrence_credits: int, semester: int, course_semesters: List[Semester]
    ) -> Optional["CourseOccurrence"]:
        if not semester:
            semester = course_semesters[0].value
        return CourseOccurrence.objects.get_or_create(
            course=course, year=year, credits=occurrence_credits, semester=semester
        )[0]

    def create_course_groups(
        self, course: Course, year: int, course_semesters: List[Semester], occurrence_credits: int, raw_group: dict
    ):
        group_mark = raw_group["group"].replace(" ", "")
        group_class_type = parse_group_type(raw_group["type"]).value
        class_num = len(raw_group["semester"])
        teachers = expand_teacher_list(raw_group["lecturer"], class_num)
        try:
            group_semester = parse_group_semester(raw_group["semester"]).value
        except Exception as e:
            log.info(f"No group semester for {course.course_number}: {e}")
            group_semester = None
        occurrence = self.occurrence_for_semester(
            course, year, occurrence_credits, group_semester, course_semesters
        )
        group, created = ClassGroup.objects.get_or_create(
            occurrence=occurrence, class_type=group_class_type, mark=group_mark
        )
        if created:
            log.info(f"Group {group.id} created")
        # Add classes to group
        for i, raw_semester in enumerate(raw_group["semester"]):
            self.create_course_class(group, i, raw_group, raw_semester, teachers)

    def create_course_class(self, group: ClassGroup, i, raw_group, raw_semester, teachers):
        # TODO: This does not handle 2 teachers for 1 group case (course 1920)
        teacher = parse_teacher(teachers[i])
        try:
            semester = parse_lesson_semester(raw_semester).value
        except Exception as e:
            semester = group.occurrence.semester
        try:
            day = parse_day_of_week(raw_group["day"][i]).value
        except Exception as e:
            log.warning(f"Skipping day for course {group.occurrence.course.course_number}: {e}")
            day = DayOfWeek.UNDEFINED.value
        try:
            start_time, end_time = parse_times(raw_group["hour"][i])
        except Exception as e:
            log.warning(f"Skipping times for course {group.occurrence.course.course_number}: {e}")
            start_time, end_time = None, None
        try:
            hall = parse_hall(raw_group["hall"][i])
        except Exception as e:
            log.warning(f"Skipping hall for course {group.occurrence.course.course_number}: {e}")
            hall = None
        course_class, created = CourseClass.objects.get_or_create(
            group=group,
            teacher=teacher,
            semester=semester,
            day=day,
            start_time=start_time,
            end_time=end_time,
            hall=hall,
        )
        if created:
            log.info(f"Class {course_class.id} created")

    def get_course_html(self, year, course_id):
        cache_path = path.join(self.cache_dir, f"{course_id}-{year}.html")
        if self.use_cache and path.exists(cache_path):
            with open(cache_path, encoding=CHARSET) as file:
                log.info(f"Reading cache for {course_id} year {year}")
                return file.read()
        data = urllib.parse.urlencode(
            {"peula": "Simple", "maslul": "0", "shana": "0", "year": year, "course": course_id}
        ).encode("utf-8")

        req = urllib.request.urlopen(url=self.shnaton_url, data=data)
        html = req.read().decode(req.headers.get_content_charset())
        with open(cache_path, "w", encoding=CHARSET) as file:
            log.info(f"Writing cache for {course_id} year {year}")
            file.write(html)
        return html

    def extract_data_from_shnaton(self, year: int, course_id: int) -> Optional[dict]:
        html = self.get_course_html(year, course_id)
        source = BeautifulSoup(html, "html.parser")

        if len(source.find_all(class_="courseTD")) == 0:
            log.warning(f"Skipping course {course_id} because of bad html")
            # course not found
            return None

        course = dict()
        # parse faculty and school
        self.parse_faculty(source, course)
        if "faculty" not in course or "school" not in course:
            log.warning(f"Skipping course {course_id} because of bad html")
            # course faculty / school not found
            return None

        # parse general course info
        self.parse_general_course_info(source, year, course)

        # parse lessons info
        self.parse_lessons(source, course)

        return course

    def parse_faculty(self, source, course):
        faculty_container = source.find(class_="courseTitle")
        if len(faculty_container) == 0:
            return

        # maxsplit = 1 because some faculties have more than one colon
        data = faculty_container.string.split(":", maxsplit=1)
        if len(data) == 2:
            course["faculty"] = data[0]
            course["school"] = data[1]

    def parse_general_course_info(self, source, year, course):
        # get general course info elements
        general_course_info = source.find_all(class_="courseTD")

        course["id"] = re.sub("[^0-9]", "", general_course_info[2].string)
        course["name"] = general_course_info[1].string
        try:
            course["name_en"] = general_course_info[0].string.title()
        except Exception as e:
            pass
        course["year"] = year
        course["semester"] = general_course_info[7].string
        course["nz"] = re.sub("[^0-9]", "", general_course_info[6].string)

    def parse_lessons(self, source, course):
        # get course lessons elements
        course_lessons = source.find_all(class_="courseDet")

        lessons = list()

        # the actual number of cells, without comment cells etc.
        actual_cell_num = len(course_lessons) - (len(course_lessons) % LESSON_TABLE_CELL_NUM)

        for i in range(0, actual_cell_num, LESSON_TABLE_CELL_NUM):
            lesson = dict()
            lesson["hall"] = parse_halls(course_lessons[i])
            lesson["hour"] = parse_hours(course_lessons[i + 2])
            lesson["day"] = parse_days(course_lessons[i + 3])
            lesson["semester"] = parse_semester(course_lessons[i + 4])
            lesson["group"] = course_lessons[i + 5].string
            lesson["type"] = course_lessons[i + 6].string
            lesson["lecturer"] = parse_lecturers(course_lessons[i + 7])

            lessons.append(lesson)

        course["lessons"] = lessons

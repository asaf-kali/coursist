import os
import re
import urllib
from datetime import date, datetime
from os import path
from typing import Optional, List, Tuple
from urllib import request
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.db.transaction import atomic
from django.utils import timezone

from academic_helper.logic.errors import ShnatonParserError, FetchRawDataError, HtmlFormatError
from academic_helper.models import Course, Faculty, Department, University
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
from academic_helper.utils.logger import log, wrap

SHNATON_URL = "https://shnaton.huji.ac.il/index.php"
CHARSET = "windows-1255"


# Edge cases:
# 34209 - Has comments
# 96203 - Has date מועדים מיוחדים
# 71080 - Has verbose מועדים מיוחדים
# 34209 - Has two teachers for the same group, one for a lesson.


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


def parse_course_credits(year: int, raw_data: dict) -> int:
    occurrence_year = int(raw_data["year"])
    if occurrence_year != year:
        raise ShnatonParserError(f"Year mismatch: given {wrap(year)}, parsed {wrap(occurrence_year)}")
    occurrence_credits = int(raw_data["nz"])
    return occurrence_credits


def parse_teachers(teachers_str: List[str]) -> List[Teacher]:
    teachers = list()
    for teacher in teachers_str:
        teachers.append(Teacher.objects.get_or_create(name=teacher)[0])
    return teachers


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
        if lecturer.string is not None and lecturer.string.strip() != "":
            ret.append(lecturer.string)
        elif lecturer.name == "br" and lecturer.previous_sibling not in ret:
            ret.append(ret[-1])
    return ret


def parse_special_occurrences(occurrences):
    if not occurrences:
        return []
    return occurrences.text.strip().split()


LESSON_TABLE_CELL_NUM = 8  # number of <td>s in the lesson table rows


def parse_lessons(source, course):
    # get course lessons elements
    course_lessons = source.find_all(class_="courseDet")

    lessons = list()

    # the actual number of cells, without comment cells etc.
    actual_cell_num = len(course_lessons) - (len(course_lessons) % LESSON_TABLE_CELL_NUM)

    for i in range(0, actual_cell_num, LESSON_TABLE_CELL_NUM):
        lesson = dict()
        lesson["hall"] = parse_halls(course_lessons[i])
        lesson["special_occurrences"] = parse_special_occurrences(course_lessons[i + 1])
        lesson["hour"] = parse_hours(course_lessons[i + 2])
        lesson["day"] = parse_days(course_lessons[i + 3])
        lesson["semester"] = parse_semester(course_lessons[i + 4])
        lesson["group"] = course_lessons[i + 5].string
        lesson["type"] = course_lessons[i + 6].string
        lesson["lecturer"] = parse_lecturers(course_lessons[i + 7])

        lessons.append(lesson)

    course["lessons"] = lessons


def parse_general_course_info(source, year, course):
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
    notes_candidates = source.find_all(class_="courseDet", colspan="8")
    if notes_candidates:
        notes = " ".join(notes_candidates[0].text.strip().split())
        if len(notes.replace("הערות:", "")) < 3:
            notes = None
        course["notes"] = notes


def parse_faculty(source, course):
    faculty_container = source.find(class_="courseTitle")
    if len(faculty_container) == 0:
        raise HtmlFormatError("Faculty / department not found")
    # maxsplit = 1 because some faculties have more than one colon
    data = faculty_container.string.split(":", maxsplit=1)
    if len(data) != 2:
        raise HtmlFormatError(f"Faculty / department bad formatting: {data}")
    course["faculty"] = data[0]
    course["department"] = data[1]


def create_course_class(group: ClassGroup, i: int, raw_group: dict, raw_semester: str, teacher: Teacher):
    try:
        semester = parse_lesson_semester(raw_semester).value
    except Exception:
        semester = group.occurrence.semester
    try:
        day = parse_day_of_week(raw_group["day"][i]).value
    except Exception as e:
        log.warning(f"Skipping day: {e}")
        day = DayOfWeek.UNDEFINED.value
    try:
        start_time, end_time = parse_times(raw_group["hour"][i])
    except Exception as e:
        log.warning(f"Skipping times: {e}")
        start_time, end_time = None, None
    try:
        hall = parse_hall(raw_group["hall"][i])
    except Exception as e:
        log.warning(f"Skipping hall: {e}")
        hall = None
    special_occurrence = None
    notes = None
    if len(raw_group["special_occurrences"]) > i:
        raw = raw_group["special_occurrences"][i]
        try:
            special_occurrence = datetime.strptime(raw, "%d/%m/%y").date()
        except Exception as e:
            log.warning(f"Skipping special occurrence: {e}")
            notes = raw
    course_class, created = CourseClass.objects.get_or_create(
        group=group,
        semester=semester,
        day=day,
        start_time=start_time,
        end_time=end_time,
        hall=hall,
        teacher=teacher,
        special_occurrence=special_occurrence,
    )
    if created:
        log.info(f"Class {course_class.id} created")
    course_class.notes = notes
    course_class.save()
    return course_class


def occurrence_for_semester(
    course: Course, year: int, occurrence_credits: int, semester: int, course_semesters: List[Semester], notes: str
) -> Optional["CourseOccurrence"]:
    if not semester:
        semester = course_semesters[0].value
    occurrence, _ = CourseOccurrence.objects.get_or_create(
        course=course, year=year, credits=occurrence_credits, semester=semester
    )
    # At this point, `course` contains the most recent name, so this is fine
    occurrence.name = course.name
    if notes:
        occurrence.notes = notes
    occurrence.save()
    return occurrence


def create_course_groups(
    course: Course,
    year: int,
    course_semesters: List[Semester],
    occurrence_credits: int,
    occurrence_notes: str,
    raw_group: dict,
):
    group_mark = raw_group["group"]
    if group_mark is not None:
        group_mark = group_mark.replace(" ", "")
    group_class_type = parse_group_type(raw_group["type"]).value
    teachers = parse_teachers(raw_group["lecturer"])
    try:
        group_semester = parse_group_semester(raw_group["semester"]).value
    except Exception as e:
        log.info(f"No group semester: {e}")
        group_semester = None
    occurrence = occurrence_for_semester(
        course, year, occurrence_credits, group_semester, course_semesters, occurrence_notes
    )
    group, created = ClassGroup.objects.get_or_create(
        occurrence=occurrence, class_type=group_class_type, mark=group_mark
    )
    if teachers and created:
        group.teachers.add(*teachers)
    if not created and teachers and set(teachers) != set(group.teachers.all()):
        group.teachers.set(teachers)
        log.info(f"Group {group.id} was updated")

    if created:
        log.info(f"Group {group.id} created")
    # Add classes to group
    first_teacher = None if not teachers else teachers[0]
    old_classes = set(CourseClass.objects.filter(group=group))
    new_classes = set()
    for i, raw_semester in enumerate(raw_group["semester"]):
        course_class = create_course_class(group, i, raw_group, raw_semester, first_teacher)
        new_classes.add(course_class)
    irrelevant_classes = old_classes - new_classes
    for c in irrelevant_classes:
        log.info(f"Class {c.id} is deleted")
        c.delete()


class ShnatonParser:
    def __init__(
        self, shnaton_url: str = SHNATON_URL, cache_dir: str = None, cache_read: bool = True, cache_write: bool = True
    ):
        self.shnaton_url = shnaton_url
        if not cache_dir:
            cache_dir = path.join("academic_helper", "shnaton_cache")
        self.cache_dir = cache_dir
        if not path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_read = cache_read
        self.cache_write = cache_write

    def get_course_html(self, year: int, course_number: int) -> str:
        cache_path = path.join(self.cache_dir, f"{course_number}-{year}.html")
        if self.cache_read and path.exists(cache_path):
            log.info("Cache read is on and file already exist, reading")
            with open(cache_path, encoding=CHARSET) as file:
                return file.read()
        log.info("Cache read is off or file does not exist yet")
        data = urllib.parse.urlencode(
            {"peula": "Simple", "maslul": "0", "shana": "0", "year": year, "course": course_number}
        ).encode("utf-8")

        response = urllib.request.urlopen(url=self.shnaton_url, data=data)
        html = response.read().decode(response.headers.get_content_charset())
        if self.cache_write:
            with open(cache_path, "w", encoding=CHARSET) as file:
                log.info(f"Writing html cache")
                file.write(html)
        else:
            log.info("Skipping cache write")
        return html

    def extract_data_from_shnaton(self, year: int, course_number: int) -> Optional[dict]:
        html = self.get_course_html(year, course_number)
        source = BeautifulSoup(html, "html.parser")
        if len(source.find_all(class_="courseTD")) == 0:
            raise HtmlFormatError(f"Course number {course_number} not found")
        raw_data = dict()
        parse_faculty(source, raw_data)
        parse_general_course_info(source, year, raw_data)
        parse_lessons(source, raw_data)
        return raw_data

    @atomic
    def _fetch_course(self, course_number: int, year: int) -> Course:
        log.info(f"Fetch course called for number {wrap(course_number)} and year {wrap(year)}")
        if not isinstance(course_number, int):
            course_number = int(course_number)

        raw_data = self.extract_data_from_shnaton(year, course_number)
        if raw_data is None:
            raise FetchRawDataError("No raw data could be parsed")

        raw_faculty = raw_data["faculty"].strip(" :\t")
        raw_department = raw_data["department"].strip(" :\t")
        huji, _ = University.objects.get_or_create(
            abbreviation="HUJI", name="האוניברסיטה העברית", english_name="The Hebrew University of Jerusalem"
        )
        faculty, _ = Faculty.objects.get_or_create(name=raw_faculty, university=huji)
        department, _ = Department.objects.get_or_create(name=raw_department, faculty=faculty)

        raw_course_number = int(raw_data["id"])
        if raw_course_number != course_number:
            raise ShnatonParserError(
                f"Course numbers mismatch: given {wrap(course_number)}, parsed {wrap(raw_course_number)}"
            )
        raw_course_name = raw_data["name"].replace("_", "")
        # if "name_en" in raw_data and len(raw_data["name_en"].replace(" ", "")) > 5:
        #     course_name = raw_data["name_en"]
        course, _ = Course.objects.get_or_create(course_number=course_number, university=huji)
        course.department = department
        course.name = raw_course_name
        course.save()

        course_semesters = parse_course_semester(raw_data["semester"])
        occurrence_credits = parse_course_credits(year, raw_data)

        for raw_group in raw_data["lessons"]:
            create_course_groups(course, year, course_semesters, occurrence_credits, raw_data["notes"], raw_group)
        return course

    def fetch_course(self, course_number: int, year: int = None) -> Course:
        """
        Fetch course from Shnaton, add it to the database and return it.
        :param course_number: The course number to search.
        :param year: The year to look for in the shnaton.
        :return: The course model object of the fetched course and its classes,
         or None if the course wasn't found.
        """
        if not year:
            now = timezone.now()
            year = now.year
            if now.month >= 8:
                year += 1
        try:
            return self._fetch_course(course_number, year)
        except ShnatonParserError:
            raise
        except Exception as e:
            raise ShnatonParserError(f"Failed to parse course {wrap(course_number)} for year {wrap(year)}") from e

import re
import urllib
from typing import Optional, List, Tuple
from urllib import request
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from academic_helper.models import Course
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

SERVER_URL = "https://shnaton.huji.ac.il/index.php"
CHARSET = "windows-1255"


def parse_course_semester(semester: str) -> List[Semester]:
    if semester == "סמסטר א' או/ו ב'":
        return [Semester.A, Semester.B]
    elif semester == "סמסטר א'":
        return [Semester.A]
    elif semester == "סמסטר ב'":
        return [Semester.B]
    elif semester == "קיץ":
        return [Semester.SUMMER]
    elif semester == "שנתי":
        return [Semester.YEARLY]
    raise NotImplementedError(f"Unrecognized semester: {semester}")


def parse_lesson_semester(semester: str) -> Semester:
    if semester == "סמסטר א":
        return Semester.A
    elif semester == "סמסטר ב":
        return Semester.B
    elif semester == "קיץ":
        return Semester.SUMMER
    elif semester == "שנתי":
        return Semester.YEARLY
    raise NotImplementedError(f"Unrecognized semester: {semester}")


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
        campus = Campus(name=match[2])
        campus.save()
        hall = Hall(name=match[1], campus=campus)
    else:
        hall = Hall(name=raw_hall)
    hall.save()
    return hall


def expand_teacher_list(teachers: List[str], length: int) -> List[str]:
    if len(teachers) == length:
        return teachers
    if len(teachers) > length:
        raise ValueError("Cannot make list shorter")
    while len(teachers) < length:
        # TODO: Is this how its working?
        teachers.insert(0, teachers[0])
    return teachers


def parse_teacher(teacher: str) -> Teacher:
    return Teacher.objects.get_or_create(name=teacher)[0]


class ShnatonParser:
    LESSON_TABLE_CELL_NUM = 8  # number of <td>s in the lesson table rows

    @staticmethod
    def fetch_course(course_number: int, year: int = 2020):
        """
        Fetch course from Shnaton, add it to the database and return it.
        :param course_number: The course number to search.
        :param year: The year to look for in the shnaton.
        :return: The course model object of the fetched course and its classes,
         or None if the course wasn't found.
        """
        if not isinstance(course_number, int):
            return None

        raw_data = ShnatonParser.extract_data_from_shnaton(year, course_number)
        if raw_data is None:
            return None

        course = Course()
        course.course_number = raw_data["id"]
        course.name = raw_data["name"]
        course.save()

        semesters = parse_course_semester(raw_data["semester"])
        for semester in semesters:
            occurrence = CourseOccurrence()
            occurrence.course = course
            occurrence.year = raw_data["year"]
            assert str(occurrence.year) == str(year)
            occurrence.semester = semester.value
            occurrence.credits = raw_data["nz"]
            occurrence.save()

        for raw_group in raw_data["lessons"]:
            # Add groups
            group = ClassGroup()
            group.mark = raw_group["group"]
            group.class_type = parse_group_type(raw_group["type"]).value
            class_num = len(raw_group["hall"])
            teachers = expand_teacher_list(raw_group["lecturer"], class_num)
            group_semester = parse_group_semester(raw_group["semester"])
            occurrence = CourseOccurrence.for_semester(course=course, year=year, semester=group_semester.value)
            group.occurrence = occurrence
            group.save()
            # Add classes to group
            for i, raw_hall in enumerate(raw_group["hall"]):
                course_class = CourseClass()
                course_class.group = group
                course_class.teacher = parse_teacher(teachers[i])
                course_class.semester = parse_lesson_semester(raw_group["semester"][i]).value
                course_class.day = parse_day_of_week(raw_group["day"][i]).value
                course_class.start_time, course_class.end_time = parse_times(raw_group["hour"][i])
                course_class.hall = parse_hall(raw_hall)
                course_class.save()

    @staticmethod
    def get_course_html(year, course_id):
        data = urllib.parse.urlencode(
            {"peula": "Simple", "maslul": "0", "shana": "0", "year": year, "course": course_id}
        ).encode(
            "utf-8"
        )  # TODO maybe windows-1255

        req = urllib.request.urlopen(url=SERVER_URL, data=data)
        html = req.read().decode(req.headers.get_content_charset())

        return html

    @staticmethod
    def extract_data_from_shnaton(year: int, course_id: int) -> Optional[dict]:
        source = BeautifulSoup(ShnatonParser.get_course_html(year, course_id), "html.parser")

        if len(source.find_all(class_="courseTD")) == 0:
            # course not found
            return None

        course = dict()
        # parse general course info
        ShnatonParser.parse_general_course_info(source, year, course)

        # parse lessons info
        ShnatonParser.parse_lessons(source, course)

        return course

    @staticmethod
    def parse_general_course_info(source, year, course):
        # get general course info elements
        general_course_info = source.find_all(class_="courseTD")

        course["id"] = re.sub("[^0-9]", "", general_course_info[2].string)
        course["name"] = general_course_info[1].string
        course["year"] = year
        course["semester"] = general_course_info[7].string
        course["nz"] = re.sub("[^0-9]", "", general_course_info[6].string)

    @staticmethod
    def parse_lessons(source, course):
        # get course lessons elements
        course_lessons = source.find_all(class_="courseDet")

        lessons = list()

        # the actual number of cells, without comment cells etc.
        actual_cell_num = len(course_lessons) - (len(course_lessons) % ShnatonParser.LESSON_TABLE_CELL_NUM)

        for i in range(0, actual_cell_num, ShnatonParser.LESSON_TABLE_CELL_NUM):
            lesson = dict()
            lesson["hall"] = ShnatonParser.parse_halls(course_lessons[i])
            lesson["hour"] = ShnatonParser.parse_hours(course_lessons[i + 2])
            lesson["day"] = ShnatonParser.parse_days(course_lessons[i + 3])
            lesson["semester"] = ShnatonParser.parse_semester(course_lessons[i + 4])
            lesson["group"] = course_lessons[i + 5].string
            lesson["type"] = course_lessons[i + 6].string
            lesson["lecturer"] = ShnatonParser.parse_lecturers(course_lessons[i + 7])

            lessons.append(lesson)

        course["lessons"] = lessons

    @staticmethod
    def parse_halls(halls):
        ret = list()
        hall_children = halls.find_all("b")

        for hall in hall_children:
            ret.append(hall.string)

        return ret

    @staticmethod
    def parse_hours(hours):
        ret = list()

        for hour in hours.contents:
            if hour.string is not None:
                # not <br>, append it
                ret.append(hour.string)

        return ret

    @staticmethod
    def parse_days(days):
        ret = list()

        for day in days.contents:
            if day.string is not None:
                # not <br>, append it
                ret.append(day.string)

        return ret

    @staticmethod
    def parse_semester(semesters):
        ret = list()

        for semester in semesters.contents:
            if semester.string is not None:
                # not <br>, append it
                ret.append(semester.string)

        return ret

    @staticmethod
    def parse_lecturers(lecturers):
        ret = list()

        for lecturer in lecturers.contents:
            if lecturer.string is not None:
                # not <br>, append it
                ret.append(lecturer.string)

        return ret

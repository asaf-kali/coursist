import os
from datetime import time
from unittest.mock import patch, MagicMock

from django.test import TestCase

from academic_helper.logic.errors import ShnatonParserError
from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models.course import Course
from academic_helper.models.course_occurrence import (
    CourseOccurrence,
    ClassGroup,
    CourseClass,
    Semester,
    ClassType,
    DayOfWeek,
)

MOCK_URL = "127.0.0.1/mock/"
COURSE_1 = 96203
COURSE_2 = 34209
NON_EXISTING_COURSE = 123456
YEAR = 2020


class TestShnatonParser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mock_dir = os.path.join("academic_helper", "tests", "mocks")
        cls.parser = ShnatonParser(MOCK_URL, mock_dir, cache_read=True, cache_write=False)

    def test_simple_base_models(self):
        # First, call the parser.
        # The parser should look for the cached .html file, which exists, and parse it.
        self.parser.fetch_course(COURSE_1, YEAR)

        # Assert base models are created as needed
        try:
            course = Course.objects.get(course_number=COURSE_1)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course {COURSE_1}: {e}")

        try:
            occurrence = CourseOccurrence.objects.get(course=course)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course occurrence: {e}")

        groups = ClassGroup.objects.filter(occurrence=occurrence)
        self.assertEquals(len(groups), 1, f"Course {COURSE_1} has exactly 1 group")
        group = groups[0]

        classes = CourseClass.objects.filter(group=group)
        self.assertEquals(len(classes), 14, "There are 14 classes")

    def test_create_multiple_groups(self):
        self.parser.fetch_course(COURSE_2, YEAR)

        try:
            course = Course.objects.get(course_number=COURSE_2)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course {COURSE_2}: {e}")
        self.assertEquals(course.name, "סוגיות מחקר בחינוך")

        try:
            occurrence = CourseOccurrence.objects.get(course=course)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course occurrence: {e}")
        self.assertEquals(occurrence.year, YEAR)
        self.assertEquals(occurrence.semester, Semester.B.value)

        groups = ClassGroup.objects.filter(occurrence=occurrence)
        self.assertEquals(len(groups), 3, f"Course {COURSE_2} has 3 groups")
        self.assertIn(groups[0].mark, "(א)")
        self.assertIn(groups[1].mark, "(א)")  # No, this is not a mistake.
        self.assertIn(groups[2].mark, "(ב)")
        self.assertEquals(groups[0].class_type, ClassType.LECTURE.value)
        self.assertEquals(groups[1].class_type, ClassType.RECITATION.value)
        self.assertEquals(groups[2].class_type, ClassType.RECITATION.value)

        classes_1 = CourseClass.objects.filter(group=groups[0])
        self.assertEquals(len(classes_1), 1)
        lecture = classes_1[0]
        self.assertEquals(lecture.day, DayOfWeek.TUESDAY.value)
        self.assertEquals(lecture.start_time, time(8, 30))
        self.assertEquals(lecture.end_time, time(10, 15))
        self.assertEquals(lecture.hall.name, "282 חינוך")
        self.assertEquals(lecture.hall.campus.name, "הר הצופים")

        classes_2 = CourseClass.objects.filter(group=groups[1])
        self.assertEquals(len(classes_2), 1)
        rec_1 = classes_2[0]
        self.assertEquals(rec_1.day, DayOfWeek.TUESDAY.value)
        self.assertEquals(rec_1.start_time, time(10, 30))
        self.assertEquals(rec_1.end_time, time(11, 15))
        self.assertEquals(rec_1.hall.name, "440 חינוך")
        self.assertEquals(rec_1.hall.campus.name, "הר הצופים")

        classes_3 = CourseClass.objects.filter(group=groups[2])
        self.assertEquals(len(classes_3), 1)
        rec_2 = classes_3[0]
        self.assertEquals(rec_2.day, DayOfWeek.TUESDAY.value)
        self.assertEquals(rec_2.start_time, time(11, 30))
        self.assertEquals(rec_2.end_time, time(12, 15))
        self.assertEquals(rec_2.hall.name, "442 חינוך")
        self.assertEquals(rec_2.hall.campus.name, "הר הצופים")

    @patch("urllib.request.urlopen", autospec=True)
    def test_shnaton_web_call(self, urlopen_mock: MagicMock):
        # This is the data the parser should call with to the shnaton
        data = f"peula=Simple&maslul=0&shana=0&year={YEAR}&course={NON_EXISTING_COURSE}".encode("utf-8")
        # These rows are here to make the urlopen function return an empty .html,
        # So the parser will quit
        mock_read = MagicMock()
        mock_read.decode.return_value = ""
        mock_response = MagicMock()
        mock_response.read.return_value = mock_read
        urlopen_mock.return_value = mock_response
        # Call the parser, assert it fails
        self.assertRaises(ShnatonParserError, self.parser.fetch_course, NON_EXISTING_COURSE, YEAR)
        first_call = urlopen_mock.call_args[1]
        self.assertEquals(first_call["url"], MOCK_URL, "Shnaton parser should call mock url")
        self.assertEquals(first_call["data"], data, "Snatom parser should pass correct search data")

        def try_to_get_non_existing_course():
            return Course.objects.get(course_number=NON_EXISTING_COURSE)

        self.assertRaises(Course.DoesNotExist, try_to_get_non_existing_course)

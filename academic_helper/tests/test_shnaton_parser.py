import os

from django.test import TestCase

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.models import Course, ClassGroup, CourseClass, CourseOccurrence, Semester

COURSE_1 = 96203


class TestShnatonParser(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parser = ShnatonParser("", os.path.join("academic_helper", "tests", "mocks"), True)

    def test_fetch_courses_creates_base_instances(self):
        self.parser.fetch_course(COURSE_1, 2020)

        try:
            course = Course.objects.get(course_number=COURSE_1)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course {COURSE_1}: {e}")

        try:
            occurrence = CourseOccurrence.objects.get(course=course)
        except (Course.MultipleObjectsReturned, Course.DoesNotExist) as e:
            self.fail(f"There must be exactly 1 course occurrence: {e}")
        self.assertEquals(occurrence.year, 2020)
        self.assertEquals(occurrence.semester, Semester.A.value)

        groups = ClassGroup.objects.filter(occurrence=occurrence)
        self.assertEquals(len(groups), 1, f"Course {COURSE_1} has exactly 1 group")
        group = groups[0]
        self.assertIn(group.mark, "(א)", "First group is Alef")

        classes = CourseClass.objects.filter(group=group)
        self.assertEquals(len(classes), 14, "There are 14 classes")

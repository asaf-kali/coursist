from django.test import TestCase

from academic_helper.logic import courses as courses_logic
from academic_helper.models import Course, Faculty, Department, University


class TestCoursesLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        uni = University.objects.create(name="האוניברסיטה השקרית", english_name="Bla bla", abbreviation="bbznot")
        faculty = Faculty.objects.create(name="הפקולטה למדעי החרטוט", university=uni)
        department = Department.objects.create(name='ביה"ס להנדסת חרטוטים', faculty=faculty)
        Course.objects.create(name="Testing 101", course_number=1000, department=department, university=uni)
        Course.objects.create(name="מבוא לחארטה", course_number=67101, department=department, university=uni)
        Course.objects.create(name="Infinitesimal Bullshit", course_number=99999, department=department, university=uni)

    def test_search_by_course_name(self):
        result = courses_logic.search("Test")
        self.assertEquals(len(result), 1)

        result = courses_logic.search("מבוא")
        self.assertEquals(len(result), 1)

        result = courses_logic.search("i")
        self.assertEquals(len(result), 2)

        result = courses_logic.search("מדעי המחשב")
        self.assertEquals(len(result), 0)

    def test_search_by_course_number(self):
        result = courses_logic.search("10")
        self.assertEquals(len(result), 2)

        result = courses_logic.search("999")
        self.assertEquals(len(result), 1)

        result = courses_logic.search("1234567")
        self.assertEquals(len(result), 0)

    def test_search_by_department(self):
        result = courses_logic.search("", "הנדסת")
        self.assertEquals(len(result), 3)

        result = courses_logic.search("חארטה", "הנדסת")
        self.assertEquals(len(result), 1)

    def test_search_by_faculty(self):
        pass  # TODO: Complete

    def test_search_with_teacher(self):
        pass  # TODO: Complete

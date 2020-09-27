from django.db.models import Q

from academic_helper.models.course import Course
from academic_helper.models.course_occurrence import (
    CourseOccurrence,
    Teacher,
    CourseClass,
)
from academic_helper.utils.logger import wrap, log


def search_occurrence(text: str):
    occurrences = CourseOccurrence.objects.filter(name__icontains=text)
    course_numbers = occurrences.values_list("course__course_number", flat=True).order_by().distinct()
    return Course.objects.filter(course_number__in=course_numbers)


def search_teacher(name: str):
    teachers = Teacher.objects.filter(name__contains=name)
    classes = CourseClass.objects.filter(teacher__in=teachers)
    course_numbers = classes.values_list("group__occurrence__course__course_number", flat=True).distinct()
    return Course.objects.filter(course_number__in=course_numbers)


def search(text: str, department: str = "", faculty: str = ""):
    log.info(f"Searching for {wrap(text)}, department {wrap(department)}, faculty {wrap(faculty)}")
    courses = Course.objects.filter(
        (Q(_name__icontains=text) | Q(course_number__icontains=text))
        & Q(department__name__contains=department)
        & Q(department__faculty__name__contains=faculty)
    )
    if len(text) >= 3:
        courses |= search_occurrence(text)
        courses |= search_teacher(text)
    return courses

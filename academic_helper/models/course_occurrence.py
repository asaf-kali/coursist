from datetime import time
from typing import Optional

from django.db import models

from academic_helper.models import Base, Course
from academic_helper.models.base import ChoicesEnum


class Semester(ChoicesEnum):
    A = 1
    B = 2
    C = 3
    SUMMER = 4
    YEARLY = 5


class ClassType(ChoicesEnum):
    LECTURE = 1
    RECITATION = 2
    SEMINAR = 3
    LAB = 4
    WORKSHOP = 5
    ASSIGNMENT = 6
    CLINICAL = 7
    TRIP = 8
    PREPARATORY = 9
    GUIDANCE = 10
    GUIDANCE_AND_LECTURE = 11

    # ("lecture", "שיעור"),  # שעור
    # ("recitation", "תרגיל"),  # תרג
    # שיעור ותרגיל
    # ("", "סמינריון"),  # סמ
    # שיעור וסמינריון
    # ("lab", "מעבדה"),  # מעב
    # ("guidance", "הדרכה"),  # הדר
    # ("guidance and lecture", "שיעור ומעבדה"),  # שומ
    # ("preparatory", "מכינה"),  # מכי
    # ("workshop", "סדנה"),  # סדנה
    # ("trip", "סיור"),  # סיור
    # ("assignment", "מטלה"),  # מטלה
    # ("clinical", "שיעור קליני"),  # שק
    # שיעור והדרכה
    # סיור-מחנה
    # ("practical work", "עבודה מעשית"),  # ע.מע
    # מחנה
    # שיעור וסדנה
    # שיעור תרגיל ומעבדה


class DayOfWeek(ChoicesEnum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7


class CourseOccurrence(Base):
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year: int = models.IntegerField()
    semester: int = models.IntegerField(choices=Semester.list())
    credits: int = models.IntegerField()

    class Meta:
        unique_together = ["course", "year", "semester"]

    def __str__(self):
        return f"{self.course} - {self.year} {Semester(self.semester).readable_name}"

    @staticmethod
    def for_semester(course: Course, year: int, semester: Semester) -> Optional["CourseOccurrence"]:
        result = CourseOccurrence.objects.filter(course=course, year=year, semester=semester).first()
        if result:
            return result
        return CourseOccurrence.objects.filter(course=course, year=year, semester=Semester.YEARLY).first()


class Campus(Base):
    name: str = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "campuses"

    def __str__(self):
        return self.name


class Hall(Base):
    name: str = models.CharField(max_length=100)
    campus: Campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.campus is not None and isinstance(self.campus, str):
            self.campus = Campus.objects.get_or_create(name=self.campus)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}{f' ({self.campus})' if self.campus else ''}"


class Teacher(Base):
    name: str = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ClassGroup(Base):
    occurrence = models.ForeignKey(CourseOccurrence, on_delete=models.CASCADE)
    class_type = models.IntegerField(choices=ClassType.list())
    mark = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.occurrence} - {ClassType(self.class_type).readable_name} ({self.mark})"


class CourseClass(Base):
    group: ClassGroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    teacher: Teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    semester: int = models.IntegerField(choices=Semester.list(), null=True, blank=True)
    day: int = models.IntegerField(choices=DayOfWeek.list(), null=True)
    start_time: time = models.TimeField()
    end_time: time = models.TimeField()
    hall: Hall = models.ForeignKey(Hall, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "course classes"

    def save(self, *args, **kwargs):
        if self.hall is not None and isinstance(self.hall, str):
            self.hall = Hall.objects.get_or_create(name=self.hall)[0]
        if self.teacher is not None and isinstance(self.teacher, str):
            self.teacher = Teacher.objects.get_or_create(name=self.teacher)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group} - {DayOfWeek(self.day).readable_name} {self.hall}"

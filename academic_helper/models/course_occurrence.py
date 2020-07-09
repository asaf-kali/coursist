from datetime import time

from django.db import models

from academic_helper.models.course import Course
from academic_helper.models.base import Base, ChoicesEnum


class Semester(ChoicesEnum):
    A = 1
    B = 2
    C = 3
    SUMMER = 4
    YEARLY = 5


class ClassType(ChoicesEnum):
    LECTURE = 1  # שעור
    RECITATION = 2  # תרג
    SEMINAR = 3  # סמ
    LAB = 4  # מעב
    WORKSHOP = 5
    ASSIGNMENT = 6  # מטלה
    CLINICAL = 7  # שק
    TRIP = 8  # סיור
    PREPARATORY = 9  # מכי
    GUIDANCE = 10  # הדר
    LESSON_AND_LAB = 11  # שומ
    SHUT = 12  # שות
    PRACTICAL_WORK = 13  # ע.מע
    LESSON_AND_WORKSHOP = 14  # שוסד
    LESSON_AND_GUIDANCE = 15  # שוה
    LESSON_AND_SEMINAR = 16  # שוס
    CAMP = 17  # מחנה


class DayOfWeek(ChoicesEnum):
    UNDEFINED = -1
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
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return f"{self.occurrence} - {ClassType(self.class_type).readable_name} ({self.mark})"

    class Meta:
        unique_together = ["occurrence", "class_type", "mark"]

    @property
    def as_dict(self) -> dict:
        result = super().as_dict
        result["teachers"] = [str(teacher) for teacher in self.teachers.all()]
        return result


class CourseClass(Base):
    group: ClassGroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    teacher: Teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    semester: int = models.IntegerField(choices=Semester.list(), null=True, blank=True)
    day: int = models.IntegerField(choices=DayOfWeek.list(), null=True, blank=True)
    start_time: time = models.TimeField(null=True, blank=True)
    end_time: time = models.TimeField(null=True, blank=True)
    hall: Hall = models.ForeignKey(Hall, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "course classes"

    @property
    def as_dict(self) -> dict:
        result = super().as_dict
        result["teacher"] = str(self.teacher)
        result["hall"] = str(self.hall)
        return result

    def __str__(self):
        return f"{self.group} - {DayOfWeek(self.day).readable_name} {self.hall}"

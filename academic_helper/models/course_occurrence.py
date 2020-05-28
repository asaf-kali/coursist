from django.db import models

from academic_helper.models import Base, Course
from academic_helper.models.base import ChoicesEnum


class Semester(ChoicesEnum):
    A = 1
    B = 2
    C = 3
    SUMMER = 4
    YEARLY = 5


class CourseOccurrence(Base):
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year: int = models.IntegerField()
    semester: int = models.IntegerField(choices=Semester.list())

    class Meta:
        unique_together = ["course", "year", "semester"]


class CourseClass(models.Model):
    course = models.ForeignKey(CourseOccurrence, on_delete=models.CASCADE)
    serial_number = models.IntegerField()  # equiv of group
    lecturer = models.CharField(max_length=100)
    class_type = models.CharField(max_length=100)
    group = models.CharField(max_length=50)
    day = models.CharField(max_length=30)
    hour = models.CharField(max_length=30)
    hall = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "course classes"

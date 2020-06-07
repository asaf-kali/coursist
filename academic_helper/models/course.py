from __future__ import annotations

from typing import Union, Collection

from django.db import models
from django.db.models import QuerySet, Q

from academic_helper.models.base import Base
from academic_helper.models.extended_rating import RatingDummy


# class University(Base):
#     name: str = models.CharField(max_length=50)
#
#     class Meta:
#         verbose_name_plural = "universities"
#
#     def str(self):
#         return self.name


class Faculty(Base):
    name: str = models.CharField(max_length=50)
    # university: University = models.ForeignKey(University, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "faculties"

    def __str__(self):
        return self.name


class School(Base):
    name: str = models.CharField(max_length=50)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if isinstance(self.faculty, str):
            self.faculty = Faculty.objects.get_or_create(name=self.faculty)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.faculty}"


class Course(Base):
    course_number: int = models.IntegerField()
    name: str = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["course_number"]

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if isinstance(self.school, str):
            self.school = School.objects.get_or_create(name=self.school)[0]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.course_number})"

    @staticmethod
    def all_courses() -> Union[Collection[Course], QuerySet]:
        return Course.objects.all()

    @property
    def semester_rating(self):
        return RatingDummy.dummy_for(self, "Semester")

    @property
    def finals_rating(self):
        return RatingDummy.dummy_for(self, "Finals")

    @property
    def interesting_rating(self):
        return RatingDummy.dummy_for(self, "Interesting")

    @staticmethod
    def find_by(text: str):
        return Course.objects.filter(Q(name__contains=text) | Q(course_number__icontains=text)).all()

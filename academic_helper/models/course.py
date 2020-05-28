from __future__ import annotations

from typing import Union, Iterable, Collection

from django.db import models
from django.db.models import QuerySet

from academic_helper.models.base import Base
from academic_helper.models.extended_rating import RatingDummy


class Faculty(Base):
    class Meta:
        verbose_name_plural = "faculties"

    name: str = models.CharField(max_length=50)


class Course(Base):
    course_number: int = models.IntegerField(unique=True)
    name: str = models.CharField(max_length=100, unique=True)
    credits: int = models.IntegerField(default=0)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["course_number"]

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if isinstance(self.faculty, str):
            self.faculty = Faculty.objects.get_or_create(name=self.faculty)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.course_number} - {self.name}"

    @staticmethod
    def get_course_by_name(title: str) -> Union[Iterable[Course], QuerySet]:
        return Course.objects.filter(title=title)

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
    def find_by(name: str):
        return Course.objects.filter(name__contains=name).all()

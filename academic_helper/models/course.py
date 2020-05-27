from __future__ import annotations

from typing import Union, Iterable, Collection

from django.db.models import IntegerField, CharField, QuerySet, ManyToManyField, ForeignKey, \
    CASCADE, SET_NULL

from academic_helper.models import ExtendedUser
from academic_helper.models.base import Base
from academic_helper.models.extended_rating import RatingDummy


class Faculty(Base):
    class Meta:
        verbose_name_plural = "faculties"

    name: str = CharField(max_length=50)


class Course(Base):
    course_number: int = IntegerField(unique=True)
    name: str = CharField(max_length=100, unique=True)
    credits: int = IntegerField(default=0)
    faculty = ForeignKey(Faculty, on_delete=SET_NULL, null=True, blank=True)

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


class StudyBlock(Base):
    name: str = CharField(max_length=50)
    courses = ManyToManyField(Course)
    min_credits: int = IntegerField()

    def __str__(self):
        return f"{self.name} Block"


class CompletedCourse(Base):
    user: ExtendedUser = ForeignKey(ExtendedUser, on_delete=CASCADE)
    course: Course = ForeignKey(Course, on_delete=CASCADE)
    block: StudyBlock = ForeignKey(StudyBlock, on_delete=CASCADE)
    grade: int = IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "course")

from __future__ import annotations

from typing import Union, Collection

from django.db import models
from django.db.models import QuerySet, Q
from star_ratings.models import Rating

from academic_helper.models.base import Base
from academic_helper.models.extended_rating import RatingDummy


class University(Base):
    abbreviation: str = models.CharField(max_length=10)
    name: str = models.CharField(max_length=150)
    english_name: str = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.abbreviation


class Faculty(Base):
    name: str = models.CharField(max_length=50)
    university: University = models.ForeignKey(University, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "faculties"

    def __str__(self):
        return self.name


class Department(Base):
    name: str = models.CharField(max_length=50)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        if isinstance(self.faculty, str):
            self.faculty = Faculty.objects.get_or_create(name=self.faculty)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.faculty}"


class Course(Base):
    course_number: int = models.IntegerField()
    _name: str = models.CharField(max_length=150, null=True, blank=True)
    university: University = models.ForeignKey(University, on_delete=models.CASCADE)
    department: Department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ["course_number", "university"]
        ordering = ["course_number"]

    def save(self, *args, **kwargs):
        if self._name:
            self.name = self.name.title()
        if isinstance(self.department, str):
            self.department = Department.objects.get_or_create(name=self.department)[0]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.course_number} | {self.name}"

    @property
    def name(self):
        if self._name:
            return self._name
        from academic_helper.models import CourseOccurrence

        return CourseOccurrence.get_latest_course_name(self.course_number)

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def as_dict(self) -> dict:
        result = super().as_dict
        del result["_name"]
        result["score"] = self.score
        result["name"] = self.name
        return result

    @staticmethod
    def all_courses() -> Union[Collection[Course], QuerySet]:
        return Course.objects.all()

    @property
    def semester_rating(self) -> RatingDummy:
        return RatingDummy.dummy_for(self, "Semester")

    @property
    def finals_rating(self) -> RatingDummy:
        return RatingDummy.dummy_for(self, "Finals")

    @property
    def interesting_rating(self) -> RatingDummy:
        return RatingDummy.dummy_for(self, "Interesting")

    @property
    def score(self) -> float:
        dummies = RatingDummy.dummies_for(self, ("Semester", "Finals", "Interesting")).values_list("id", flat=True)
        ratings = Rating.objects.filter(Q(object_id__in=dummies) & Q(content_type__model="ratingdummy") & ~Q(count=0))
        if not ratings.exists():
            return 0
        return sum(ratings.values_list("average", flat=True)) / len(ratings)

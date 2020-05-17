from __future__ import annotations

from typing import Union, Iterable, Collection

from django.db.models import IntegerField, CharField, QuerySet

from reviews.models.base import Base


class Course(Base):
    course_number: int = IntegerField(unique=True)
    title: str = CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.title = self.title.title()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.course_number} - {self.title}"

    @staticmethod
    def get_course_by_name(title: str) -> Union[Iterable[Course], QuerySet]:
        return Course.objects.filter(title=title)

    @staticmethod
    def all_courses() -> Union[Collection[Course], QuerySet]:
        return Course.objects.all()

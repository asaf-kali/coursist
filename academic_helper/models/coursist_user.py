from typing import Union

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404

from academic_helper.models.base import Base
from academic_helper.utils.logger import log, wrap


class CoursistUser(AbstractUser, Base):
    degree_program: "DegreeProgram" = models.ForeignKey(
        "academic_helper.DegreeProgram", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        log.info(f"Saving user: {wrap(self)}")

    def set_degree_program(self, program: Union[int, "DegreeProgram"]):
        if isinstance(program, int):
            self.degree_program_id = program
        else:
            self.degree_program = program
        self.save()

    @staticmethod
    def get_by_username(username):
        queryset = CoursistUser.objects.filter(username=username)
        return get_object_or_404(queryset)

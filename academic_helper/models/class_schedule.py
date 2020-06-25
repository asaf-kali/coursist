from django.db import models

from academic_helper.models.base import Base
from academic_helper.models.coursist_user import CoursistUser
from academic_helper.models.course_occurrence import ClassGroup


class ClassSchedule(Base):
    user: CoursistUser = models.ForeignKey(CoursistUser, on_delete=models.CASCADE)
    group: ClassGroup = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.group}"

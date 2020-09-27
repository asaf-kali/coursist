from typing import Iterable

from django.db import models

from academic_helper.models.base import Base
from academic_helper.models.course import Course
from academic_helper.models.course_occurrence import CourseOccurrence
from academic_helper.models.coursist_user import CoursistUser
from academic_helper.utils.logger import wrap, log


class StudyBlock(Base):
    name: str = models.CharField(max_length=50)
    courses: Iterable[Course] = models.ManyToManyField(Course)
    min_credits: int = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


class UserCourseChoice(Base):
    user: CoursistUser = models.ForeignKey(CoursistUser, on_delete=models.CASCADE)
    course: CourseOccurrence = models.ForeignKey(CourseOccurrence, on_delete=models.CASCADE)
    block: StudyBlock = models.ForeignKey(StudyBlock, on_delete=models.SET_NULL, null=True, blank=True)
    grade: int = models.IntegerField(null=True, blank=True)
    is_completed: bool = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.user} - {self.course}"

    @staticmethod
    def move_course(user_id, course_id, block_id):
        log.info(f"Moving course {wrap(course_id)} into block {wrap(block_id)} for user {wrap(user_id)}")
        choice, created = UserCourseChoice.objects.get_or_create(user_id=user_id, course_id=course_id)
        if created:
            log.info(f"Choice created")
        else:
            log.info(f"Choice already existed at block {wrap(choice.block_id)}")
        choice.block_id = block_id
        choice.save()


class DegreeProgram(Base):
    name: str = models.CharField(max_length=50)
    code: int = models.IntegerField()
    blocks = models.ManyToManyField(StudyBlock)
    credits: int = models.IntegerField()
    is_public: bool = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} | {self.name}"

    @staticmethod
    def public_programs():
        return DegreeProgram.objects.filter(is_public=True)

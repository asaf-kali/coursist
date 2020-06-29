from typing import List, Union

from django.contrib.sites.models import Site
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django_comments.abstracts import CommentAbstractModel
from star_ratings.models import UserRating

from academic_helper.models import Course
from academic_helper.utils.logger import log, wrap


class CourseComment(CommentAbstractModel):
    is_anonymous = models.BooleanField(
        "is anonymous", default=False, help_text="Check this box if we should hide the user name."
    )
    year = models.CharField("year", max_length=10, blank=True)
    semester = models.CharField("semester", max_length=10, blank=True)

    @property
    def get_user_name_to_show(self):
        """
        :return: The user name to be shown in the comments list - either user name or 'Anonymous'
        """
        return self.user_name if not self.is_anonymous else "Anonymous"

    @property
    def get_semester_name_to_show(self):
        """
        :return: The user name to be shown in the comments list - either user name or 'Anonymous'
        """
        return f"{self.year} {self.semester}"

    @property
    def course(self) -> Course:
        return Course.objects.get(pk=self.object_pk)

    @property
    def semester_rating(self):
        return self.course.semester_rating.get_user_rating(self.user)

    @property
    def finals_rating(self):
        return self.course.finals_rating.get_user_rating(self.user)

    @property
    def interesting_rating(self):
        return self.course.interesting_rating.get_user_rating(self.user)

    def __str__(self):
        return f"{self.name}: {self.comment[:50]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        log.info(f"Comment saved: {wrap(self)}")

    @staticmethod
    def for_user(user_id) -> Union[QuerySet, List["CourseComment"]]:
        return CourseComment.objects.filter(user_id=user_id)

    @staticmethod
    def set_anonymous(comment_id, is_anonymous: bool):
        comment = get_object_or_404(CourseComment, id=comment_id)
        comment.is_anonymous = is_anonymous
        comment.save()

from django.db import models
from django_comments.abstracts import CommentAbstractModel

from star_ratings.models import UserRating
from academic_helper.models import Course


class CourseComment(CommentAbstractModel):
    is_anonymous = models.BooleanField(
        "is anonymous", default=False, help_text="Check this box if we should hide the  user name."
    )

    @property
    def get_user_name_to_show(self):
        """
        :return: The user name to be shown in the comments list - either user name or 'Anonymous'
        """
        return self.user_name if not self.is_anonymous else "Anonymous"

    @property
    def semester_rating(self):
        course = Course.objects.get(pk=self.object_pk)
        return UserRating.objects.get(user=self.user, rating=course.semester_rating)

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

    def get_rating_score(self, rating_dummy):
        semester_rating = UserRating.objects.filter(user=self.user, rating__object_id=rating_dummy.id)
        if len(semester_rating) == 1:
            return semester_rating[0].score
        if len(semester_rating) == 0:
            return -1
        assert 0, 'There should be no more than 1 on these.'

    @property
    def semester_rating(self):
        course = Course.objects.get(pk=self.object_pk)
        return self.get_rating_score(course.semester_rating)

    @property
    def finals_rating(self):
        course = Course.objects.get(pk=self.object_pk)
        return self.get_rating_score(course.finals_rating)

    @property
    def interesting_rating(self):
        course = Course.objects.get(pk=self.object_pk)
        return self.get_rating_score(course.interesting_rating)

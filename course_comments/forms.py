from django import forms
from django.utils import timezone
from django_comments.forms import CommentForm

from academic_helper.models import Semester
from course_comments.models import semester_name

YEAR_CHOICES = [(y, f"{y - 1}/{y}") for y in range(2016, timezone.now().year)]
SEMESTER_CHOICES = [(v, semester_name(v)) for v in Semester.values()]
SEMESTER_CHOICES.pop(2)  # This is a HUJI only patch.


class CourseCommentForm(CommentForm):
    is_anonymous = forms.BooleanField(required=False)
    comment = forms.CharField(label="Comment", widget=forms.Textarea())
    year = forms.IntegerField(label="year", widget=forms.Select(choices=reversed(YEAR_CHOICES)))
    semester = forms.IntegerField(label="semester", widget=forms.Select(choices=SEMESTER_CHOICES))

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the title field
        data = super(CourseCommentForm, self).get_comment_create_data(site_id=site_id)
        data["is_anonymous"] = self.cleaned_data["is_anonymous"]
        data["year"] = self.cleaned_data["year"]
        data["semester"] = self.cleaned_data["semester"]
        return data

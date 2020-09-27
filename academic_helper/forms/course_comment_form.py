from django import forms
from django.utils import timezone
from django_comments.forms import CommentForm

from academic_helper.models.course_comment import semester_name
from academic_helper.models.course_occurrence import Semester

year = timezone.now().year
YEAR_CHOICES = [(None, "לא נבחר")] + [(y, f"{y}/{y + 1}") for y in range(year - 1, year - 7, -1)]
SEMESTER_CHOICES = [(None, "לא נבחר")] + [(v, semester_name(v)) for v in Semester.values()]
SEMESTER_CHOICES.pop(3)  # This is a HUJI only patch.


class CourseCommentForm(CommentForm):
    is_anonymous = forms.BooleanField(required=False)
    comment = forms.CharField(widget=forms.Textarea())
    year = forms.IntegerField(widget=forms.Select(choices=YEAR_CHOICES), required=False)
    semester = forms.IntegerField(widget=forms.Select(choices=SEMESTER_CHOICES), required=False)

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the title field
        data = super().get_comment_create_data(site_id=site_id)
        data["is_anonymous"] = self.cleaned_data["is_anonymous"]
        data["year"] = self.cleaned_data["year"]
        data["semester"] = self.cleaned_data["semester"]
        return data

from django import forms
from django_comments.forms import CommentForm
import datetime

now = datetime.datetime.now()
current_year = now.year % 100
if now.month < 9:
    current_year -= 1
YEAR_CHOICES = [(f"20{y}", f"20{y}/{y + 1}") for y in range(16, current_year + 1)][::-1]

SEMESTER_CHOICES = [
    ("א", "א"),
    ("ב", "ב"),
    ("קיץ", "קיץ"),
    ("שנתי", "שנתי"),
]


class CourseCommentForm(CommentForm):
    is_anonymous = forms.BooleanField(required=False)
    comment = forms.CharField(label="Comment", widget=forms.Textarea())
    year = forms.CharField(label="year", widget=forms.Select(choices=YEAR_CHOICES))
    semester = forms.CharField(label="semester", widget=forms.Select(choices=SEMESTER_CHOICES))

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the title field
        data = super(CourseCommentForm, self).get_comment_create_data(site_id=site_id)
        data["is_anonymous"] = self.cleaned_data["is_anonymous"]
        data["year"] = self.cleaned_data["year"]
        data["semester"] = self.cleaned_data["semester"]
        return data

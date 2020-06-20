from django import forms
from django_comments.forms import CommentForm


class CourseCommentForm(CommentForm):
    is_anonymous = forms.BooleanField(required=False)
    show_email = forms.BooleanField(required=False, initial=True)

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the title field
        data = super(CourseCommentForm, self).get_comment_create_data(site_id=site_id)
        data["is_anonymous"] = self.cleaned_data["is_anonymous"]
        data["show_email"] = self.cleaned_data["show_email"]
        return data

from django import forms
from django_comments.forms import CommentForm


class CourseCommentForm(CommentForm):
    is_anonymous = forms.BooleanField(required=False)
    comment = forms.CharField(label='Comment', widget=forms.Textarea({'cols': '70', 'rows': '7'}))

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the title field
        data = super(CourseCommentForm, self).get_comment_create_data(site_id=site_id)
        data["is_anonymous"] = self.cleaned_data["is_anonymous"]
        return data

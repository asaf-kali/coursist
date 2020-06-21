from django.contrib.auth.forms import PasswordResetForm
from django import forms


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget = forms.EmailInput(attrs={
            'placeholder': 'אימייל',
            'autofocus': 'autofocus',
            'class': 'form-control'})
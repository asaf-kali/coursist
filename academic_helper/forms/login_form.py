from allauth.account.forms import LoginForm
from django import forms


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["login"].widget = forms.TextInput(
            attrs={"placeholder": "שם משתמש או אימייל", "autofocus": "autofocus", "class": "form-control",}
        )

        self.fields["password"].widget = forms.PasswordInput(attrs={"placeholder": "סיסמה", "class": "form-control"})

        self.fields["remember"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})

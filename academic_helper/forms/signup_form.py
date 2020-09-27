from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget = forms.TextInput(
            attrs={"placeholder": "אימייל", "autofocus": "autofocus", "class": "form-control",}
        )

        self.fields["username"].widget = forms.TextInput(
            attrs={"placeholder": "שם משתמש", "autofocus": "autofocus", "class": "form-control",}
        )

        self.fields["password1"].widget = forms.PasswordInput(attrs={"placeholder": "סיסמה", "class": "form-control"})

        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"placeholder": "אימות סיסמה", "class": "form-control"}
        )

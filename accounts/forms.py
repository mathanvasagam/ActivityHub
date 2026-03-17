from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "Username or email"}))

    def clean(self):
        identifier = (self.cleaned_data.get("username") or "").strip()
        if identifier and "@" in identifier:
            user = get_user_model().objects.filter(email__iexact=identifier).first()
            if user:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()


class ForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField()


class VerifyResetCodeForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=6, min_length=6, help_text="Enter the 6-digit code sent to your email.")

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise forms.ValidationError("Code must be 6 digits.")
        return code


class ResetPasswordWithCodeForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New password")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("new_password1")
        pwd2 = cleaned_data.get("new_password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

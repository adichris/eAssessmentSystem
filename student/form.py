from django import forms
from .models import Student
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator


class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("index_number", "level", 'programme')
        error_messages = {
            "index_number": {
                "unique": "this Index number is not available.",
                "max_length": "This index number is not accepted ( has more than 60 character)",
            }
        }

    def __init__(self, lecture=None, *args, **kwargs):
        super(StudentRegisterForm, self).__init__(*args, **kwargs)
        if lecture is not None:
            try:
                self.fields["programme"].queryset = lecture.department.programme_set.all()
            except Exception:
                pass


class PasswordSetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        MinimumLengthValidator(min_length=4).validate(password=password)
        return password

    def clean_password_confirm(self):
        pwd = self.cleaned_data.get("password")
        pwd_confirm = self.cleaned_data.get("password_confirm")

        if not (pwd == pwd_confirm):
            raise forms.ValidationError("Confirm password must match.")
        return pwd_confirm

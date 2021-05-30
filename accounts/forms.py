from django import forms
from .models import User
import datetime

dateMax = datetime.date.today().year - 10
DOY = tuple(x+1 for x in range(1979, dateMax, 1))


class UserCreateForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_number", "email", "dob", "password")
        widgets = {
            "password": forms.PasswordInput,
            "dob":forms.SelectDateWidget(years=DOY)
        }

        error_messages = {
            "first_name": {
                "null": "first name is required",
                "max_length": "Staff first name length is too much",
            },
            "last_name": {
                "null": "your last name is required",
            },
            "username": {
                "null": "username is required",
                "unique": "this username already exists",
            },
            "phone_number": {
                "null": "phone number is required",
                "unique": "this phone number already exists",
            },
            "email": {
                "null": "email is required",
                "unique": "this email already exists",
            },

            "password": {
                "min_length": "Your password length is too small",
                "max_length": "Your password length is too much"
            }

        }

    def clean_password2(self):
        pwd = self.cleaned_data.get("password")
        pwd2 = self.cleaned_data.get("password2")

        if pwd != pwd2:
            return forms.ValidationError("Password does not match")
        return pwd2

    def save(self, commit=False):
        # Change the value of commit to False in other to make changes
        instance = super(UserCreateForm, self).save(False)
        instance.set_password(self.cleaned_data.get("password"))
        instance.save()

        return instance


class StudentProfileCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "email", "dob")
        widgets = {
            "password": forms.PasswordInput,
            "dob":forms.SelectDateWidget(years=DOY)
        }

        error_messages = {
            "first_name": {
                "null": "first name is required",
                "max_length": "Staff first name length is too much",
            },
            "last_name": {
                "null": "your last name is required",
            },

            "phone_number": {
                "null": "phone number is required",
                "unique": "this phone number already exists",
            },
            "email": {
                "null": "email is required",
                "unique": "this email already exists",
            },

        }


class StudentLoginForm(forms.Form):
    index_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

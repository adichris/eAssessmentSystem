from django import forms
from .models import User
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import datetime


def clean_dob(self):
    dob = self.cleaned_data.get("dob")
    """
        Student date of birth can not be less than 9 year 
    """
    today = datetime.date.today()
    if dob is None:
        raise forms.ValidationError("Please enter your date of birth.")

    if dob >= datetime.date(year=today.year - 9, month=today.month, day=today.day):
        raise forms.ValidationError("Sorry we can not accept this as your date of birth. Your too young.")
    return dob


class UserCreateForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_number", "email", "dob", "password")
        widgets = {
            "password": forms.PasswordInput,
            "dob": forms.DateInput(attrs={"type": "date"}),
            "phone_number": PhoneNumberPrefixWidget(attrs={"class":"form-control", "type": "tel"})
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

    def clean_dob(self):
        return clean_dob(self)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "email", "dob",)
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "phone_number": PhoneNumberPrefixWidget(attrs={"class":"form-control", "type": "tel"})
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

    def clean_dob(self):
        return clean_dob(self)


class StudentProfileCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "email", "dob")
        widgets = {
            "password": forms.PasswordInput,
            "dob": forms.DateInput(attrs={"type": "date"}),
            "phone_number":PhoneNumberPrefixWidget(attrs={"class": "form-control", "type": "tel"})
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

    def clean_dob(self):
        return clean_dob(self)


class StudentLoginForm(forms.Form):
    index_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ConfirmResetPasswordForm(forms.Form):
    username = forms.CharField(help_text="account username or index number")
    first_name = forms.CharField(max_length=60)
    last_name = forms.CharField(max_length=60)
    phone_number = forms.CharField(widget=PhoneNumberPrefixWidget(attrs={"class":"form-control", "type": "tel"}))
    dob = forms.CharField(max_length=60, widget=forms.DateInput(attrs={"type": "date"}), label="Date of birth")


class PasswordSetForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("password", "confirm_password")

        widgets = {
        "password": forms.PasswordInput(attrs={"value": ""})
        }

    def __init__(self, *args, **kwargs):
        super(PasswordSetForm, self).__init__(*args, **kwargs)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        cn_pwd = self.cleaned_data.get("confirm_password")

        if not pwd == cn_pwd:
            raise forms.ValidationError("Password do not match!")
        return cn_pwd

    def save(self, commit=True):
        instance = super(PasswordSetForm, self).save(False)
        instance.set_password(self.cleaned_data["password"])
        if commit:
            instance.save()
        return instance


class PasswordUpdateForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label="New password confirmation")

    def clean_old_password(self):
        old_pwd = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_pwd):
            raise forms.ValidationError("Enter a correct password")

        return old_pwd

    def clean_new_password(self):
        old_pwd = self.cleaned_data.get("old_password")
        new_pwd = self.cleaned_data.get("new_password")

        from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator
        mini_pwd = MinimumLengthValidator(min_length=4)
        mini_pwd.validate(new_pwd, user=self.user)

        common_pwd = CommonPasswordValidator()
        common_pwd.validate(new_pwd, user=self.user)

        if old_pwd == new_pwd:
            raise forms.ValidationError("New password can not be the same as the old password")

        return new_pwd

    def clean_confirm_new_password(self):
        cn_pwd = self.cleaned_data.get("confirm_new_password")
        new_pwd = self.cleaned_data.get("new_password")

        if cn_pwd != new_pwd:
            raise forms.ValidationError("Password must match")

        return cn_pwd

    def __init__(self, user, *args, **kwargs):
        super(PasswordUpdateForm, self).__init__(*args, **kwargs)
        self.user = user

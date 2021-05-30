from django import forms
from .models import CourseModel


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ("name", "code", "level", "semester", "lecture", "programme")


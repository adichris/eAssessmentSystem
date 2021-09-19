from django import forms
from .models import CourseModel, CourseLevel


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ("name", "code", "level", "semester", "lecture", "programme")


class CourseLevelCreateForm(forms.ModelForm):
    class Meta:
        model = CourseLevel
        fields = ("name", "number")

        widgets = {
            "number": forms.NumberInput(attrs={"placeholder": 100})
        }

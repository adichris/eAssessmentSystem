from django import forms
from .models import CourseModel, CourseLevel


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ("name", "code", "level", "semester", "lecture", "programme")

    def __init__(self, lecturers, *args, **kwargs):
        super(CourseCreateForm, self).__init__(*args, **kwargs)
        self.fields["lecture"].queryset = lecturers


class CourseLevelCreateForm(forms.ModelForm):
    class Meta:
        model = CourseLevel
        fields = ("name", "number")

        widgets = {
            "number": forms.NumberInput(attrs={"placeholder": 100})
        }

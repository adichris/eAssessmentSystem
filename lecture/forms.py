from .models import LectureModel
from django import forms


class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = LectureModel
        fields = ("department", )

from django import forms
from .models import Department


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "short_name", "created_by")
        widgets = {
            "created_by": forms.HiddenInput
        }

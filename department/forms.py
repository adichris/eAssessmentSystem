from django import forms
from .models import Department


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "short_name", "created_by")
        widgets = {
            "created_by": forms.HiddenInput
        }


class DepartmentSetChangeHODForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("hod", )

    def __init__(self, *args, **kwargs):
        super(DepartmentSetChangeHODForm, self).__init__(*args, **kwargs)
        self.fields["hod"].queryset = kwargs["instance"].lecturemodel_set.all()

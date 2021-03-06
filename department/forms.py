from django import forms
from .models import Department


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "short_name", "created_by")
        widgets = {
            "created_by": forms.HiddenInput
        }


class DepartmentSetChangeHODForm(forms.Form):
    hod = forms.ModelChoiceField(queryset=None, required=False, label="Head of Department",
                                 help_text="Change Head of Department", empty_label="--- unknown ---")

    def clean_hod(self):
        hod = self.cleaned_data.get("hod")
        if not hod:
            raise forms.ValidationError("Please select a lecturer as HOD for the department")
        return hod

    def __init__(self, instance, *args, **kwargs):
        super(DepartmentSetChangeHODForm, self).__init__(*args, **kwargs)
        self.fields["hod"].queryset = instance.lecturemodel_set.all()

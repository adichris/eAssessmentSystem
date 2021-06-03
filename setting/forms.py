from django import forms
from .models import GeneralSetting


class GeneralSettingUpdateForm(forms.ModelForm):
    class Meta:
        model = GeneralSetting
        exclude = ( "user", )


class GeneralSettingCreateForm(forms.ModelForm):
    class Meta:
        model = GeneralSetting
        exclude = ("user", )

        widgets = {
            "user": forms.HiddenInput
        }

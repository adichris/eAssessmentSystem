from django import forms
from .models import GeneralSetting
import datetime

this_year = datetime.date.today().year
year = tuple(
    (f"{x-1} / {x}", f"{x-1} / {x}") for x in range(this_year, this_year -12, -1)
)


class GeneralSettingUpdateForm(forms.ModelForm):
    class Meta:
        model = GeneralSetting
        exclude = ("user",)

        widgets = {
            "academic_year": forms.Select(choices=year),
        }

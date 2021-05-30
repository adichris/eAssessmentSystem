from django import forms
from .models import Programme


class ProgrammeCreateForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ('name', 'department')


class ProgrammeSelectForm(forms.Form):
    programme = forms.ModelChoiceField(required=True, queryset=Programme.objects.all(), error_messages={
        "require": "Select your programme of study.",
    })

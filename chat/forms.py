from django.db import models
from django.forms import fields, widgets
from .models import Message
from django import forms


class MessageCreateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("from_user", "to_user", "message")
        widgets = {
            "from_user": forms.Select(attrs={"class": "no-pointer no-user-select"}),
            "to_user": forms.Select(attrs={"class": "no-pointer no-user-select"}),
        }

class MessageCreateInlineForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("message", )
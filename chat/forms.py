from .models import Message, CourseMessage
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


class CourseMessageCreationForm(forms.ModelForm):
    class Meta:
        model = CourseMessage
        fields = ("message", )

        widgets = {
            "message": forms.Textarea(attrs={"rows":"5"})
        }

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

#
# class GrpMsgCreateInlineForm(forms.ModelForm):
#     class Meta:
#         model = GrpMsg
#         fields = ("message", )
#
#
# class MessageGroupCreateForm(forms.ModelForm):
#     class Meta:
#         model = GroupMessage
#         fields = ("group_name", "to_group", "department", "programme", "level")
#
#     def __init__(self, user_obj=None, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         if user_obj is not None and user_obj.is_lecture:
#             lecture = user_obj.lecturemodel
#             self.fields["programme"].queryset = lecture.department.programme_set
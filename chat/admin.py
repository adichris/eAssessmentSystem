from django.contrib import admin
from .models import Message, GroupMessage
# Register your models here.


@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "timestamp")
    readonly_fields = list_display + ("message", )


@admin.register(GroupMessage)
class GroupMessageModelAdmin(admin.ModelAdmin):
    list_display = ("group_name", "from_user", "timestamp", "department", "programme", "level", "to_group")
    readonly_fields = list_display

    fieldsets = [
        ("Group Information", {"fields":("group_name", "from_user", "to_group")}),
        ("Filter", {"fields":("department", "programme", "level")})
    ]

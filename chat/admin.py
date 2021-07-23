from django.contrib import admin
from .models import Message
# Register your models here.


@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "timestamp")
    readonly_fields = list_display + ("message", )
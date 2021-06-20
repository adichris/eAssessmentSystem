from django.contrib import admin
from .models import GeneralSetting


@admin.register(GeneralSetting)
class GeneralSettingModelAdmin(admin.ModelAdmin):
    list_display = ("semester", "name_order", "academic_year",)
    readonly_fields = ("user", )


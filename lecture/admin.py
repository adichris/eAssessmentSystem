from django.contrib import admin
from .models import LectureModel
# Register your models here.


@admin.register(LectureModel)
class LectureModelAdmin(admin.ModelAdmin):
    list_display = ("profile", "department")

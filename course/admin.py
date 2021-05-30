from django.contrib import admin
from .models import CourseLevel, CourseModel


@admin.register(CourseModel)
class CourseModelAdmin(admin.ModelAdmin):
    list_filter = ("level", "semester")
    list_display = ("name", "level", "semester", "programme", "Date_Added")
    search_fields = ("name",)

    def Date_Added(self, course_model):
        return course_model.timestamp


admin.site.register(CourseLevel)

from django.contrib import admin
from .models import Programme


@admin.register(Programme)
class ProgrammeModel(admin.ModelAdmin):
    list_display = ("name", 'number_of_courses', 'department', 'timestamp')

    def number_of_courses(self, programme):
        return programme.coursemodel_set.count()


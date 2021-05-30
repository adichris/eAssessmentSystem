from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ("__str__", "number_of_programme", "created_by")

    def number_of_programme(self, department):
        return department.programme_set.count()

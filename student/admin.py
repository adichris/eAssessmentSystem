from django.contrib import admin
from .models import Student
# Register your models here.


@admin.register(Student)
class StudentModelAdmin(admin.ModelAdmin):
    list_display = ('profile', 'index_number', 'level',)
    list_filter = ("level", )

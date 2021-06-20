from django.db import models
from accounts.models import User
from django.shortcuts import reverse
from department.models import Department


class Programme(models.Model):
    """
    :Course_set programme consist of courses that student studies
    :name the programme name
    :timestamp the date and time the programme was add to the system
    :created by the user or staff who add the programme
    :keyword name, courses, timestamp, created by
    """
    name = models.CharField(max_length=250, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by", null=True)

    def __str__(self):
        return self.name.title()

    class Meta:
        ordering = ("name", "pk")

    def get_absolute_url(self):
        return reverse("department:programme:detail", kwargs={"programName": self.name, "pk": self.pk})

    def get_update_url(self):
        return reverse("department:programme:update", kwargs={"programName": self.name, "pk": self.pk})

    @property
    def all_students(self):
        return self.student_set.all()

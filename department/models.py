from django.db import models
from accounts.models import User
from django.shortcuts import reverse


class DepartmentManager(models.Manager):
    def search(self, query):
        q = models.Q(name__icontains=query) | models.Q(short_name__icontains=query)
        return self.filter(q)


class Department(models.Model):
    """
    :keyword; name, short_name, create_by, updated
    :short_name department short name to represent it
    :name department full name name maximum number of characters is 250
    :created_by user who added this department to the system
    :updated datetime the department was updated
    :programme the department programmes
    """
    name = models.CharField(max_length=250, unique=True)
    short_name = models.CharField(max_length=60, null=True, blank=True, unique=True)
    created_by = models.ForeignKey(to=User, on_delete=models.CASCADE)
    hod = models.OneToOneField(null=True, blank=True, help_text="Change Head of Department",
                               verbose_name="Head Of Department",
                               to=User, related_name="hod_user",
                               on_delete=models.CASCADE,
                               )

    updated = models.DateTimeField(auto_now=True)
    objects = DepartmentManager()

    def __str__(self):
        return self.name.title()

    def get_absolute_url(self):
        return reverse("department:detail", kwargs={"name": self.name, "pk": self.pk})

    def students_count(self):
        count = 0
        for program in self.programme_set.all():
            count += program.student_set.count()
        return count

    def lectures_count(self):
        return '---'

from django.db import models
from course.models import CourseSemester
from accounts.models import User
from django.shortcuts import reverse
from django.utils import timezone

current_year = timezone.now().date().year


class NameOrder(models.TextChoices):
    FIRSTNAME = "f", "First Name"
    LASTNAME = "l", "Last Name"


class GeneralSetting(models.Model):
    semester = models.CharField(max_length=60, choices=CourseSemester.choices,
                                help_text="The current academic semester",
                                default=CourseSemester.SEMESTER1,
                                )
    name_order = models.CharField(max_length=20, choices=NameOrder.choices,
                                  help_text="How to order your name",
                                  default=NameOrder.FIRSTNAME,
                                  )
    academic_year = models.CharField(max_length=11, default=current_year-1,
                                     help_text="Select the academic year for the semester",
                                     )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return "%s settings " % str(self.user)

    def get_absolute_url(self):
        return reverse("setting:detail", kwargs={"pk": self.id, "user_id": self.user_id})

    def get_update_url(self):
        return reverse("setting:update", kwargs={"pk": self.id, "user_id": self.user_id})

from typing import Dict
from django.db import models
from accounts.models import User
from programme.models import Programme, Department
from student.models import CourseLevel
# Create your models here.


class MassageManager(models.Manager):
    def all_for_both(self, from_user, to_user):
        msg_from = self.filter(from_user=from_user, to_user=to_user)
        msg_to = self.filter(to_user=from_user, from_user=to_user)
        return msg_from.union(msg_to)


class Message(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE, verbose_name="From", blank=True)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE, verbose_name="To", null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = MassageManager()

    def __str__(self) -> str:
        return f"Message {self.from_user} to {self.to_user} @{str(self.timestamp)} "



class GroupMessageToChoices(models.TextChoices):
    LECTURES = "lecturers", "Lecturers"
    STAFFS = "staffs", "Staffs"
    STUDENTS = "student", "Students"
    ADMINS = "admins", "Administrators"
    # all includes lecturers and students then staffs
    ALL = "all", "All"


class GroupMessage(models.Model):
    group_name = models.CharField(unique=True, max_length=60, help_text="Name of this group")
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(on_delete=models.CASCADE, to=CourseLevel, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="the sender", verbose_name="From")
    to_group = models.CharField(max_length=60, choices=GroupMessageToChoices.choices, null=True, default=GroupMessageToChoices.STUDENTS, help_text="The category of people who will be recieving this message", verbose_name="To")

    def __str__(self) -> str:
        return self.group_name
    
    def get_absolute_url(self):
        from django.shortcuts import reverse
        return reverse('chat:group_detail', kwargs={'grpid': self.id, "grpname": self.group_name})

    def get_group_members(self):
        members = User.objects.filter()
        return     


class GrpMsg(models.Model):
    title = models.CharField(null=True, max_length=120)
    message = models.TextField()
    group = models.ForeignKey(GroupMessage, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

from django.db import models
from accounts.models import User
from programme.models import Programme, Department
from course.models import CourseLevel, CourseModel
# Create your models here.


class MassageManager(models.Manager):
    def all_for_both(self, from_user, to_user):
        msg_from = self.filter(from_user=from_user, to_user=to_user)
        msg_to = self.filter(to_user=from_user, from_user=to_user)
        msg_to.update(read=True)
        return msg_from.union(msg_to)

    def count_unread(self):
        return self.filter(read=False).count()


class Message(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE, verbose_name="From", blank=True)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE, verbose_name="To", null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    objects = MassageManager()

    def __str__(self) -> str:
        return f"Message {self.from_user} to {self.to_user} @{str(self.timestamp)} "


class CourseGroupMessage(models.Model):
    course = models.OneToOneField(CourseModel, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.course.name + " Chats "


class CourseMessage(models.Model):
    message = models.TextField()
    group = models.ForeignKey(CourseGroupMessage, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.message


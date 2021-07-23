from django.db import models
from accounts.models import User
from programme.models import Programme
# Create your models here.

class ProgrammeMessage(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.user) + f" ({self.id})"
    

class MassageManager(models.Manager):
    def all_for_both(self, from_user, to_user):
        msg_from = self.filter(from_user=from_user, to_user=to_user)
        msg_to = self.filter(to_user=from_user, from_user=to_user)
        return msg_from.union(msg_to)
        


class Message(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE, verbose_name="From", blank=True)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE, verbose_name="To", blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = MassageManager()

    def __str__(self) -> str:
        return f"Message {self.from_user} to {self.to_user} @{str(self.timestamp)} "



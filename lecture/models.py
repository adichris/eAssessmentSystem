from django.db import models
from accounts.models import User
from department.models import Department
from django.shortcuts import reverse


class LectureManager(models.Manager):
    def search(self, query):
        q_str = models.Q(profile__first_name__icontains=query) | models.Q(profile__last_name__icontains=query) | models.Q(
            profile__username__contains=query)
        return self.filter(q_str).filter(profile__is_active=True)


class LectureModel(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    objects = LectureManager()

    # TODO remove programme from lectureModel
    # so lectureModel will have course_set which already has programme relation

    class Meta:
        verbose_name = "Lecture"
        verbose_name_plural = "Lectures"

    def __str__(self):
        return str(self.profile.get_full_name())

    def get_absolute_url(self):
        return reverse("lecture:detail", kwargs={"pk": self.pk})

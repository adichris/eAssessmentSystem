from django.db import models
from accounts.models import User
from course.models import CourseLevel
from programme.models import Programme
from django.shortcuts import reverse


class StudentManager(models.Manager):
    def create_student(self, first_name: str, last_name: str, phone_number, email, dob, index_number, level):
        profile = User.objects.create_user(
            first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, dob=dob,
            username=index_number,
        )
        student = self.create(index_number=index_number, profile=profile)

        return student

    def search(self, query):
        query_str = models.Q(index_number__icontains=query) | models.Q(profile__first_name__icontains=query) | models.Q(
            profile__last_name__icontains=query)
        return self.filter(query_str)

    def search_lecture_student(self, query, lecture):
        if lecture and query:
            query_str = models.Q(index_number__icontains=query) | models.Q(profile__first_name__icontains=query) | models.Q(
                profile__last_name__icontains=query)
            return self.filter(query_str)
        elif lecture:
            query_str = models.Q(programme__department=lecture.department)
            return self.filter(query_str, programme__department=lecture.department)
        else:
            return set()


class Student(models.Model):
    """
    :profile student profile detail including first and last name, phone number, etc
    :index_number student index number unique to every student
    :created_by the staff who added this student to the system

    student model will be added to department: department references the student
    """
    # TODO add student related fields (assessment profile, )
    profile = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    index_number = models.CharField(max_length=60, unique=True, null=False, blank=False)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True)
    update = models.DateField(auto_now=True)
    level = models.ForeignKey(CourseLevel, on_delete=models.CASCADE)
    objects = StudentManager()

    class Meta:
        ordering = ("programme", "level", "index_number")

    def get_name(self):
        return self.profile.get_full_name()

    def __str__(self):
        return self.index_number

    def get_absolute_url(self):
        return reverse("student:detail", kwargs={"pk": self.pk})

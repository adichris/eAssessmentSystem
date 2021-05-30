from django.db import models
from student.models import Student
from assessment.models import QuestionGroup
# Create your models here.


class StudentResults(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    score = models.IntegerField()
    # answer Scripts
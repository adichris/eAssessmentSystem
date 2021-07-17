from django.db import models
from django.shortcuts import reverse
from programme.models import Programme
from lecture.models import LectureModel


class CourseManager(models.Manager):
    def get_lecture_courses(self, lecture, programme=None):
        if programme:
            return self.filter(lecture=lecture, programme=programme, semester=lecture.profile.generalsetting.semester)
        else:
            return self.filter(lecture=lecture, semester=lecture.profile.generalsetting.semester)


class CourseLevel(models.Model):
    """
    The Level can be to access a course.
    example: Level 100 students has their core and objective course
    """
    name = models.CharField(max_length=10, verbose_name="Level name", default="level")
    number = models.IntegerField(unique=True, verbose_name="Level Number")

    class Meta:
        verbose_name = "Level"
        verbose_name_plural = "Levels"
        unique_together = ("name", "number")
        ordering = ("number",)

    def __str__(self):
        return "%s %s" % (self.name.title(), self.number)
    
    def get_students(self):
        return self.student_set.count()


class CourseSemester(models.TextChoices):
    """
    Two semesters in every institution (at least 2).
    """
    SEMESTER1 = "s1", "First Semester"
    SEMESTER2 = "s2", "Second Semester"


class CourseModel(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100, unique=True, verbose_name="code code")
    level = models.ForeignKey(CourseLevel, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, choices=CourseSemester.choices)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    lecture = models.ForeignKey(LectureModel, on_delete=models.CASCADE, null=True, blank=True)
    objects = CourseManager()

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ("level", "name")
        # unique_together = ("lecture", "programme")

    def question_conduct(self):
        return self.questiongroup_set.filter(status__in=("conducted", "marked", "published"))

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)

    def conducted_quizzes(self):
        return self.questiongroup_set.filter(status__in=("conducted", "published"))

    def get_lecture(self):
        return None

    def get_absolute_url(self):
        return reverse("department:programme:course:detail", kwargs={"courseName": self.name, "pk": self.pk})

    def get_update_url(self):
        return reverse("department:programme:course:update", kwargs={"courseName": self.name, "pk": self.pk})

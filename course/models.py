from django.db import models
from django.shortcuts import reverse
from programme.models import Programme
from lecture.models import LectureModel
from django.utils.text import slugify

class CourseManager(models.Manager):
    def get_lecture_courses(self, lecture, programme=None):
        if programme and lecture:
            # return self.filter(lecture=lecture, programme=programme, semester=lecture.profile.generalsetting.semester)
            return self.filter(lecture=lecture, programme=programme)
        elif lecture:
            # return self.filter(lecture=lecture, semester=lecture.profile.generalsetting.semester)
            return self.filter(lecture=lecture)


class CourseLevel(models.Model):
    """
    The Level can be to access a course.
    example: Level 100 students has their core and objective course
    """
    name = models.CharField(max_length=10, verbose_name="Level name", default="Level",
                            help_text="The letter part of the level")
    number = models.IntegerField(unique=True, verbose_name="Level Number", help_text="The numeric part of the level")

    class Meta:
        verbose_name = "Level"
        verbose_name_plural = "Levels"
        unique_together = ("name", "number")
        ordering = ("name", "number",)

    def __str__(self):
        return "%s %s" % (self.name.title(), self.number)
    
    def get_students(self):
        return self.student_set.count()

    def get_absolute_url(self):
        return reverse("department:programme:course:level_detail", kwargs={"pk": self.pk})

    def get_absolute_update_url(self):
        return reverse("department:programme:course:level_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse("department:programme:course:level_delete", kwargs={"pk": self.pk})


class CourseSemester(models.TextChoices):
    """
    Two semesters in every institution (at least 2).
    """
    SEMESTER1 = "s1", "First Semester"
    SEMESTER2 = "s2", "Second Semester"


class CourseModel(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100, unique=True, verbose_name="Course code")
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

    def question_conduct(self):
        return self.conducted_quizzes()

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)

    def conducted_quizzes(self):
        # return question group and join lecture GeneralSetting where academic_year is the same
        if self.lecture:
            return self.questiongroup_set.filter(status__in=("conducted", "published"), academic_year=self.lecture.profile.generalsetting.academic_year)
        else:
            return None

    def get_absolute_url(self):
        return reverse("department:programme:course:detail", kwargs={"courseName": slugify(self.name), "pk": self.pk})

    def get_update_url(self):
        return reverse("department:programme:course:update", kwargs={"courseName": slugify(self.name), "pk": self.pk})

    def get_student_studying(self):
        return self.programme.student_set.filter(level=self.level, profile__generalsetting__semester=self.semester)

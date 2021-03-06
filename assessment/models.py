from django.db import models
from course.models import CourseModel, LectureModel
from accounts.models import User
from django.shortcuts import reverse
from student.models import Student
from eAssessmentSystem.tool_utils import unique_slug_generator_scheme
from django.utils import timezone


class QuestionGroupChoice(models.TextChoices):
    QUIZ1 = "quiz1", "Quiz 1"
    QUIZ2 = "quiz2", "Quiz 2"
    QUIZ3 = "quiz3", "Quiz 3"
    QUIZ4 = "quiz4", "Quiz 4"
    QUIZ = "quiz5", "Quiz 5"
    MIDSEM = "midsem", "Mid Semester Quiz"
    __empty__ = '--------'


class QuestionTypeChoice(models.TextChoices):
    MULTICHOICE = "multichoice", "Multi Choice"
    THEORY = "theory", "Theory"
    # TheoryPlusMultiChoice = "multichoice_theory", "Theory Question and Multi Choice"


class QuestionGroupStatus(models.TextChoices):
    PREPARED = "prepared", "Prepared"
    MARKED = "marked", "Marked"
    CONDUCTED = "conducted", "Conducted"
    CONDUCT = "conduct", "Conduct"
    PUBLISHED = "published", "Published"


class ScriptStatus(models.TextChoices):
    MARKED = "marked", "Marked"
    MARKING = "marking", "Marking"
    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Submitted"
    ASSESSING = "assessing", "Assessing"
    PUBLISHED = "published", "Published"


class AssessmentPreference(models.Model):
    duration = models.DurationField(blank=True, null=True, help_text="The assessment duration in hours:minutes:seconds (eg; 0:30:00)")
    due_date = models.DateTimeField(blank=True, null=True, verbose_name="Due Date and Time - Deadline")
    is_question_shuffle = models.BooleanField(default=False, verbose_name="Shuffle Questions",
                                              help_text="Rearrange questions for each student")
    instruction = models.CharField(max_length=150, default="answer all questions",
                                   help_text="Assessment instruction. eg:ANSWER ALL QUESTIONS,")
    start_time = models.TimeField(null=True, blank=True, help_text="Assessment start time")

    def __str__(self):
        return f"{str(self.questiongroup.course.name)} ({self.questiongroup.course.level}) {self.questiongroup.get_title_display()}"
    
    class Meta:
        ordering = ("id", )


class QuestionGroup(models.Model):
    title = models.CharField(max_length=20, help_text="Assessment title example: Assignment 1 or Quiz 2")
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, help_text="The course to hold the questions")
    updated = models.DateTimeField(auto_now_add=True)
    total_marks = models.IntegerField(default=5)
    questions_type = models.CharField(max_length=20, choices=QuestionTypeChoice.choices,
                                      default=QuestionTypeChoice.MULTICHOICE)
    status = models.CharField(max_length=25, choices=QuestionGroupStatus.choices, default=QuestionGroupStatus.PREPARED)
    preference = models.OneToOneField(to=AssessmentPreference, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    is_share_total_marks = models.BooleanField(default=False, help_text="This will force share total mark on each question mark.")
    academic_year = models.CharField(max_length=20, default=f"{timezone.now().year - 1} / {timezone.now().year}")

    class Meta:
        unique_together = ("title", "course", "questions_type")
        ordering = ("pk", "title", "questions_type")

    def get_title_display(self):
        if not self.title.istitle():
            return self.title.capitalize()

        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("assessment:question_grp_detail",
                       kwargs={
                                "courseName": self.course.name,
                                "title": self.title,
                                "pk": self.pk
                            }
                       )

    def generate_marks(self, force=None):
        if force or self.is_share_total_marks or self.questions_type == QuestionTypeChoice.MULTICHOICE:
            try:
                each_mark = self.total_marks / self.question_set.count()
                for question in self.question_set.all():
                    question.max_mark = each_mark
                    question.save()
            except ZeroDivisionError:
                pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        returns = super(QuestionGroup, self).save(force_insert=force_insert, force_update=force_update,
                                                  using=using, update_fields=update_fields)
        self.generate_marks()
        return returns

    def get_completed_script(self):
        if self.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.multichoicescripts_set.filter(is_completed=True)
        elif self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.filter(is_completed=True)

    def get_scripts_average_score(self):
        if self.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.multichoicescripts_set.aggregate(average_score=models.Avg("score")).get("average_score")
        elif self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.aggregate(average_score=models.Avg("total_score")).get("average_score")

    def get_scripts_highest_score(self):
        if self.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.multichoicescripts_set.aggregate(average_score=models.Max("score")).get("average_score")
        elif self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.aggregate(average_score=models.Max("total_score")).get("average_score")

    def get_scripts_lowest_score(self):
        if self.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.multichoicescripts_set.aggregate(average_score=models.Min("score")).get("average_score")
        elif self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.aggregate(average_score=models.Min("total_score")).get("average_score")

    def get_scripts_average_score_count(self):
        average_score = self.get_scripts_average_score()
        if not average_score:
            return
        if self.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.multichoicescripts_set.filter(score__gte=average_score).count()
        elif self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.filter(total_score__gte=average_score).count()

    def fix_question_numbers(self):
        num = 0
        for question in self.question_set.order_by("id"):
            num += 1
            question.question_number = num
            question.save()

    def is_all_scripts_marked(self):
        if self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.count() == self.studenttheoryscript_set.filter(status=ScriptStatus.MARKED).count()
        return self.multichoicescripts_set.count() == self.multichoicescripts_set.filter(status=ScriptStatus.MARKED).count()

    def get_marked_scripts(self):
        if self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.filter(status=ScriptStatus.MARKED)
        return self.multichoicescripts_set.filter(status=ScriptStatus.MARKED)

    def get_unmarked_scripts(self):
        if self.questions_type == QuestionTypeChoice.THEORY:
            return self.studenttheoryscript_set.exclude(status__in=(ScriptStatus.PUBLISHED, ScriptStatus.MARKED))
        return self.multichoicescripts_set.exclude(status__in=(ScriptStatus.PUBLISHED, ScriptStatus.MARKED))

    @property
    def total_script_count(self):
        return self.multichoicescripts_set.count() + self.studenttheoryscript_set.count()

    def theory_question_without_max_mark(self):
        if self.questions_type == QuestionTypeChoice.THEORY:
            return self.question_set.filter(max_mark__isnull=True)


class QuestionManager(models.Manager):
    def order_by_question_number(self):
        return self.all().order_by("question_number")


class Question(models.Model):
    """
        fields:
        .question: The actual question text
        relationship:
        .optionchoices_set
    """
    question = models.TextField(unique=False, null=True, blank=False, help_text="the question text")
    max_mark = models.FloatField(help_text="maximum score mark for this question", null=True, blank=True,)
    group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now_add=True)
    question_number = models.IntegerField(default=None, null=True, blank=True)
    objects = QuestionManager()
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.question)

    class Meta:
        ordering = ("question_number", "id",  "updated")

    def get_absolute_delete_url(self):
        return reverse("assessment:delete_question",
                       kwargs={"group_title": self.group.title, "pk": self.pk, "coursePK": self.group.course.pk})


def automate_question_number(instance, **kwargs):
    if not instance.question_number:
        question_number = instance.group.question_set.count()
        instance.question_number = question_number + 1


models.signals.pre_save.connect(automate_question_number, sender=Question)


class MultiChoiceQuestion(models.Model):
    option = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 help_text="Multi-choice question option")
    is_answer_option = models.BooleanField(verbose_name="Answer option",
                                           help_text="Is this option is the answer?", default=False)

    class Meta:
        verbose_name = "Option Choice"
        verbose_name_plural = "Option Choices"

    def __str__(self):
        return self.option


class MultiChoiceScripts(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    time_remain = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=60, choices=ScriptStatus.choices, default=ScriptStatus.ASSESSING)
    is_completed = models.BooleanField(default=False)
    has_paused = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Multi Choice Script"
        verbose_name_plural = verbose_name + "s"

    def __str__(self):
        return "%s - %s %s" % (self.student, self.course, self.question_group.get_title_display())

    def score_student(self):
        # score = 0
        # c_answer = 0
        # for SMCA in self.studentmultichoiceanswer_set.all():
        #     for m_option in SMCA.question.multichoicequestion_set.all():
        #         if m_option.is_answer_option and m_option == SMCA.selected_option:
        #             score += SMCA.question.max_mark
        #             c_answer += 1
        #
        # self.score = score
        # self.correct_answers = c_answer
        # self.save()

        # The new way

        self.score = self.get_selected_option__is_answer_option_sum()
        if self.status not in (ScriptStatus.PUBLISHED, ScriptStatus. MARKED):
            self.status = ScriptStatus.MARKED
        self.save()
        return self.score

    def get_answered_question_queryset(self):
        self.answered_question_queryset_instance__ = self.studentmultichoiceanswer_set.filter(selected_option__isnull=False)
        return self.answered_question_queryset_instance__

    def get_selected_option__is_answer_option_sum(self):
        self.correct_answers_set = self.get_correct_answers_set()
        return sum([a.question.max_mark for a in self.correct_answers_set])

    def get_correct_answers_set(self):
        return self.studentmultichoiceanswer_set.filter(selected_option__is_answer_option=True)

    def get_wrong_answers_count(self):
        return self.question_group.question_set.count() - self.get_correct_answers_set().count()

    @property
    def is_all_marked(self):
        if self.score == 0:
            return True
        return bool(self.score)


class StudentMultiChoiceAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, )
    selected_option = models.ForeignKey(MultiChoiceQuestion, on_delete=models.CASCADE, null=True, blank=True)
    script = models.ForeignKey(MultiChoiceScripts, on_delete=models.CASCADE)

    @property
    def is_correct_answer(self):
        if self.selected_option:
            return self.selected_option.is_answer_option
    
    def __str__(self) -> str:
        return "Student MultiChoice Answer %s" % self.id


class StudentTheoryScript(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=60, choices=ScriptStatus.choices, default=ScriptStatus.ASSESSING)
    submitted_at = models.DateTimeField(blank=True, null=True)
    has_paused = models.BooleanField(default=False)
    total_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "question_group")

    @property
    def is_all_marked(self):
        return self.studenttheoryanswer_set.filter(score__isnull=False).count() == \
               self.studenttheoryanswer_set.count()

    def __str__(self):
        return "%s %s" % (self.student.get_name(), self.__class__.__name__)

    @property
    def score(self):
        return self.studenttheoryanswer_set.aggregate(models.Sum("score")).get("score__sum")

    def get_answered_question_queryset(self):
        return self.studenttheoryanswer_set.filter(score__gt=0)

    def get_wrong_answers_count(self):
        return self.studenttheoryanswer_set.filter(score=0).count()
    
    @property
    def get_total_answered(self):
        """IGNORE NONE COUNT"""
        return self.studenttheoryanswer_set.filter(answer__isnull=False)


class TheoryAnswerManager(models.Manager):
    def is_question_answered(self, question_id, script_id):
        try:
            return bool(self.get(question_id=question_id, script_id=script_id, answer__isnull=False).answer)
        except models.ObjectDoesNotExist:
            return False


class StudentTheoryAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True, unique=False, help_text="Your answer to the question.")
    script = models.ForeignKey(StudentTheoryScript, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    lecture_comment = models.TextField(null=True, blank=True, help_text="Lectures comment on answer")
    objects = TheoryAnswerManager()

    class Meta:
        ordering = ("question", "id")

    def get_absolute_solve_url(self):
        question_group = self.script.question_group
        return reverse("assessment:theory_exam_answer", kwargs={
            "question_group_title":question_group.title,
            "question_group_id":question_group.id,
            "script_pk":self.script.pk,
            "question_pk":self.question.pk
        })


class TheoryMarkingSchemeManager(models.Manager):
    def filter_lecture(self, lecture):
        return self.filter(
            lecture=lecture,
            question_group__course__in=lecture.coursemodel_set.all(),
            question_group__course__semester=lecture.profile.generalsetting.semester,
            question_group__academic_year=lecture.profile.generalsetting.academic_year,
        )


class TheoryMarkingScheme(models.Model):
    question_group = models.OneToOneField(QuestionGroup, on_delete=models.CASCADE)
    lecture = models.ForeignKey(LectureModel, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TheoryMarkingSchemeManager()

    def __str__(self):
        return f"{str(self.question_group.course)} {str(self.question_group.get_title_display())} Marking Scheme"

    def get_unsolved_question(self):
        return self.question_group.question_set.filter(solution__isnull=True)


def scheme_created(instance, created, **kwargs):
    if created:
        instance.slug = unique_slug_generator_scheme(TheoryMarkingScheme)
        instance.save()


models.signals.post_save.connect(receiver=scheme_created, sender=TheoryMarkingScheme)


class Solution(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(help_text="Solution to the question")
    notes = models.TextField(blank=True, null=True, help_text="Notes on solution")
    scheme = models.ForeignKey(TheoryMarkingScheme, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "Solution %s" % self.id
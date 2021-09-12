from lecture.models import LectureModel
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user
from eAssessmentSystem.tool_utils import (admin_required_message, get_http_forbidden_response,
                                          get_not_allowed_render_response, general_setting_not_init
                                          )
from student.models import Student
from django.utils.text import slugify
from django.utils import timezone
from .form import LectureFilterForm
from assessment.models import (QuestionGroupStatus, QuestionGroup, QuestionTypeChoice, ScriptStatus,
                               StudentTheoryScript, MultiChoiceScripts, CourseModel)
from django.db.models import ObjectDoesNotExist, Sum


class RecordsView(LoginRequiredMixin, TemplateView):
    template_name = "record/all_records.html"

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture:
            return super(RecordsView, self).get(request, *args, **kwargs)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:student_login")


class StudentRecordTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "record/student.html"

    def get_student(self):
        user = get_user(self.request)
        try:
            return user.student
        except ObjectDoesNotExist:
            return

    def get(self, request, *args, **kwargs):
        student = self.get_student()

        if student and student.programme:
            try:
                return super(StudentRecordTemplateView, self).get(request, *args, **kwargs)
            except ObjectDoesNotExist as err:
                return general_setting_not_init(request)
        elif student:
            return get_http_forbidden_response()

        elif self.request.user.is_authenticated:
            return get_http_forbidden_response()
        else:
            return redirect("accounts:student_login")

    def get_context_data(self, **kwargs):
        ctx = super(StudentRecordTemplateView, self).get_context_data(**kwargs)
        student = self.request.user.student
        ctx["courses"] = student.programme.coursemodel_set.filter(
            level=student.level,
            semester=self.request.user.generalsetting.semester
        )
        return ctx


class LectureRecordsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "record/lecture/all_records_view.html"
    filter_form_class = LectureFilterForm
    COURSE_SORT = "course"
    QUIZ_SORT = "quiz"
    SORT_NAME = "sort"

    def get_context_data(self, **kwargs):
        ctx = super(LectureRecordsTemplateView, self).get_context_data(**kwargs)
        self.filter_class = self.filter_form_class(data=self.request.GET,
                                                   lecture=self.request.user.lecturemodel)
        if self.is_quiz_sort:
            ctx["all_course_scripts"] = self.get_all_lecture_records()
        else:
            ctx["courses"] = self.get_courses()
        ctx["filter_form"] = self.filter_class
        ctx["title"] = "Records"
        ctx["is_quiz_sort"] = self.is_quiz_sort
        ctx["course_sort"] = self.COURSE_SORT
        ctx["quiz_sort"] = self.QUIZ_SORT
        ctx["sort_name"] = self.SORT_NAME
        return ctx

    def get_courses(self):
        return CourseModel.objects.filter(
            lecture=self.request.user.lecturemodel,
            semester=self.request.user.generalsetting.semester
        )

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture:
            self.is_quiz_sort = self.request.GET.get(self.SORT_NAME) == self.QUIZ_SORT
            return super(LectureRecordsTemplateView, self).get(request, *args, **kwargs)
        elif self.request.user:
            return get_not_allowed_render_response(request)
        else:
            return get_http_forbidden_response()

    def get_all_lecture_records(self):
        lecture_profile = self.request.user
        queryset_filter = dict(
            course__lecture=lecture_profile.lecturemodel,
            course__semester=lecture_profile.generalsetting.semester,
            academic_year=lecture_profile.generalsetting.academic_year,
            status__in=(QuestionGroupStatus.CONDUCTED, QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.MARKED)
        )
        if self.filter_class.is_valid():
            question_group_title = self.filter_class.cleaned_data.get("question_group_title")
            course_id = self.filter_class.cleaned_data.get("course")
            course__level = self.filter_class.cleaned_data.get("level")
            course__programme_id = self.filter_class.cleaned_data.get("programme")

            if question_group_title:
                queryset_filter["title"] = question_group_title
            if course_id:
                queryset_filter["course_id"] = course_id
            if course__programme_id:
                queryset_filter["course__programme_id"] = course__programme_id
            if course__level:
                queryset_filter["course__level"] = course__level

            return QuestionGroup.objects.filter(
                **queryset_filter
            ).order_by("course__code", "course__level")


class LectureQuizRecordDetailView(LoginRequiredMixin, DetailView):
    template_name = "record/lecture/lecture_record_detail.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            QuestionGroup,
            title=self.kwargs.get("question_group_title"),
            pk=self.kwargs.get("question_group_pk"),
            course__lecture=self.request.user.lecturemodel,
            course__code=self.kwargs.get("course_code"),
            status__in=(QuestionGroupStatus.CONDUCTED, QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.MARKED)
        )

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            return super(LectureQuizRecordDetailView, self).get(request, *args, **kwargs)
        elif self.request.user.is_admin:
            return get_not_allowed_render_response(request)

        else:
            return get_http_forbidden_response()


class LectureCourseRecords(LoginRequiredMixin, DetailView):
    model = CourseModel
    template_name = "record/lecture/course_records.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture or (self.request.user.is_hod or self.request.user.is_admin):
            self.init_instances()
            return super(LectureCourseRecords, self).get(request, *args, **kwargs)
        
        return get_not_allowed_render_response(request)
    
    def get_lecture(self):
        if self.request.user.is_lecture and not self.request.user.is_hod:
            return self.request.user.lecturemodel
        try:
            lecture_id = self.kwargs.get("lecture_id")
            return LectureModel.objects.get(id=lecture_id)
        except LectureModel.DoesNotExist:
            pass

    def get_students(self):
        return Student.objects.filter(
            programme__coursemodel=self.course_instance,
            level=self.course_instance.level,
        )

    def init_instances(self):
        self.course_instance = get_object_or_404(
            self.model,
            lecture=self.get_lecture(),
            pk=self.kwargs["course_pk"],
            code=self.kwargs["course_code"],
        )

    def get_object(self, queryset=None):
        return self.course_instance

    def get_context_data(self, **kwargs):
        ctx = super(LectureCourseRecords, self).get_context_data(**kwargs)
        ctx["is_quiz_sort"] = self.request.GET.get("sort") == "course"
        ctx["title"] = f"{self.get_object().name} - records"
        ctx["students"] = self.get_students()
        ctx["question_groups"] = self.get_questions()
        ctx["conduct_status"] = QuestionGroupStatus.CONDUCT
        ctx["conducted_status"] = QuestionGroupStatus.CONDUCTED
        ctx["theory_type"] = QuestionTypeChoice.THEORY
        ctx["is_back"] = self.request.GET.get("back")
        return ctx

    def get_questions(self):
        return self.course_instance.questiongroup_set.filter(status__in=(
            QuestionGroupStatus.CONDUCT,
            QuestionGroupStatus.CONDUCTED,
            QuestionGroupStatus.MARKED,
            QuestionGroupStatus.PUBLISHED,
        ))


class PublishRecordsDetailView(LoginRequiredMixin, DetailView):
    template_name = "lecture/publish/detailview.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instance()
            confirm_code = request.GET.get("confirm_code")

            logic1 = confirm_code and confirm_code == self.get_confirm_code()
            logic2 = self.question_group_instance.status in (QuestionGroupStatus.MARKED, QuestionGroupStatus.PUBLISHED)
            if logic1 and logic2:
                return self.publish_scripts()
            return super(PublishRecordsDetailView, self).get(request, *args, **kwargs)
        elif self.request.user.is_staff:
            return get_not_allowed_render_response(request)
        else:
            return get_http_forbidden_response()

    def publish_scripts(self):
        self.question_group_instance.status = QuestionGroupStatus.PUBLISHED
        self.question_group_instance.updated = timezone.now()
        self.question_group_instance.save()
        affected_rows = None
        if self.question_group_instance.questions_type == QuestionTypeChoice.MULTICHOICE:
            affected_rows = self.question_group_instance.multichoicescripts_set.update(status=ScriptStatus.PUBLISHED)
        elif self.question_group_instance.questions_type == QuestionTypeChoice.THEORY:
            affected_rows = self.question_group_instance.studenttheoryscript_set.update(status=ScriptStatus.PUBLISHED)
        self.request.session["publish_alert"] = affected_rows
        return redirect("lecture:question_group_detail", course_id=self.question_group_instance.course_id,
                        question_group_pk=self.question_group_instance.pk)

    def get_context_data(self, **kwargs):
        ctx = super(PublishRecordsDetailView, self).get_context_data(**kwargs)
        ctx["script_mark"] = self.get_scripts_marked()
        ctx["students_count"] = self.get_all_student_count()
        ctx["confirm_code"] = self.get_confirm_code()
        ctx["students_null_work"] = ctx["students_count"] - ctx["script_mark"]
        return ctx

    def get_confirm_code(self):
        return slugify(self.question_group_instance.question_set.first().question)

    def init_instance(self):
        self.question_group_instance = get_object_or_404(
            QuestionGroup,
            course__lecture=self.request.user.lecturemodel,
            course__semester=self.request.user.generalsetting.semester,
            academic_year=self.request.user.generalsetting.academic_year,
            pk=self.kwargs.get("question_group_pk"),
            title=self.kwargs.get("question_group_title"),
            course__code=self.kwargs.get("course_code")
        )

    def get_object(self, queryset=None):
        return self.question_group_instance

    def get_scripts_marked(self):
        if self.question_group_instance.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.question_group_instance.multichoicescripts_set.count()

        elif self.question_group_instance.questions_type == QuestionTypeChoice.THEORY:
            return self.question_group_instance.studenttheoryscript_set.count()

    def get_all_student_count(self):
        coursemodel = self.question_group_instance.course
        return Student.objects.filter(level=coursemodel.level,
                                      programme=coursemodel.programme).count()


class StudentRecordsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "record/student/course_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            if self.request.user.student:
                self.init_instances()
                return super(StudentRecordsTemplateView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(StudentRecordsTemplateView, self).get_context_data(**kwargs)
        ctx["theory_script"] = self.theory_scripts
        ctx["multichoice_script"] = self.multichoice_script
        ctx["total_score"] = self.total_score
        ctx["course"] = self.course_instance
        return ctx

    def init_instances(self):
        generalsetting = self.request.user.generalsetting
        self.course_instance = CourseModel.objects.get(
            code=self.kwargs.get("course_code"),
            semester=generalsetting.semester,
            id=self.kwargs.get("course_id")
        )

        self.theory_scripts = StudentTheoryScript.objects.filter(
            question_group__course=self.course_instance,
            student=self.request.user.student,
            status=ScriptStatus.PUBLISHED,
            question_group__academic_year=generalsetting.academic_year,
            question_group__status=QuestionGroupStatus.PUBLISHED
        )
        self.multichoice_script = MultiChoiceScripts.objects.filter(
            question_group__academic_year=generalsetting.academic_year,
            student=self.request.user.student,
            course_id=self.course_instance.id,
            question_group__status=QuestionGroupStatus.PUBLISHED,
            status=ScriptStatus.PUBLISHED
        )

        thoery_total_score_sum = self.theory_scripts.aggregate(total_score_sum=Sum("total_score")).get("total_score_sum")
        multichoice_score_sum = self.multichoice_script.aggregate(score_sum=Sum("score")).get("score_sum")
        self.total_score = 0
        if thoery_total_score_sum is not None:
            self.total_score = thoery_total_score_sum
        if multichoice_score_sum is not None:
            self.total_score += multichoice_score_sum

from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import LectureModel
from .forms import LectureCreateForm, StudentTheoryAnswer, StudentAnswerMarkForm, FilterForms, QuestionGroupFilterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView
from accounts.forms import UserCreateForm
from django.forms import inlineformset_factory
from eAssessmentSystem.tool_utils import (admin_required_message, get_http_forbidden_response, get_status_tips,
                                          get_not_allowed_render_response
                                          )
from assessment.models import (QuestionGroup, QuestionGroupStatus, CourseModel, TheoryMarkingScheme,
                               Question, Solution, QuestionTypeChoice, ScriptStatus, StudentTheoryScript
                               )
from assessment.form import LectureQuestionSolutionForm
from django.utils.html import format_html
from django.db.models import ObjectDoesNotExist
from django.utils.http import is_safe_url
from department.models import Department


class LectureCreateView(LoginRequiredMixin, View):
    model = LectureModel
    lecture_form_class = LectureCreateForm
    profile_form = UserCreateForm
    template_name = "lecture/add.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            ctx = {
                "lecture_form": self.lecture_form_class(),
                "profile_form": self.profile_form(),
                "pageTitle": "Add Lecture"
            }
            return render(request, template_name=self.template_name, context=ctx)
        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:admin-login-page")

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            lecture_form = self.lecture_form_class(request.POST)
            profile_form = self.profile_form(request.POST)
            if lecture_form.is_valid() and profile_form.is_valid():
                profile_ins = profile_form.save(False)
                profile_ins.is_lecture = True
                profile_ins.save()
                lecture_ins = lecture_form.save(False)
                lecture_ins.profile = profile_ins
                lecture_ins.save()
                request.session["lecture_created_pk"] = lecture_ins.pk
                return redirect("lecture:created")
            ctx = {
                "lecture_form": lecture_form,
                "profile_form": profile_form,
                "pageTitle": "Add Lecture",
                "number_has_error": profile_form.has_error("phone_number"),
                "number_error": profile_form.errors.get("phone_number"),
            }
            return render(request, self.template_name, ctx)


@login_required
def lecture_created_view(request):
    lecture_pk = request.session.get("lecture_created_pk")
    if request.user.is_staff and lecture_pk:
        lecture = get_object_or_404(LectureModel, pk=lecture_pk)
        ctx = {
            "lecture": lecture
        }
        # del request.session["lecture_created_pk"]
        return render(request, "lecture/created.html", ctx)
    return redirect("landing-page")


class LectureDetailView(LoginRequiredMixin, DetailView):
    model = LectureModel
    template_name = "lecture/detail.html"

    def get(self, request, *args, **kwargs):
        user = self.request.user
        is_lecturer = self.get_object() == user
        if (user.is_staff and user.is_admin) or (is_lecturer and user.is_active):
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "%s Detail" % self.object
        ctx["profile"] = self.object.profile
        ctx["courses_ctn"] = self.object.coursemodel_set.count()
        ctx["courses"] = self.object.coursemodel_set.all()
        return ctx


class LectureListView(LoginRequiredMixin, ListView):
    model = LectureModel
    template_name = "lecture/list.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(LectureListView, self).get(request, *args, **kwargs)

        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:admin-login-page")

    def get_context_data(self, object_list=None, **kwargs):
        ctx = super(LectureListView, self).get_context_data(object_list=object_list, **kwargs)
        ctx["query"] = self.request.GET.get("query")
        return ctx

    def get_queryset(self):
        query = self.request.GET.get("query")
        if query:
            return self.model.objects.search(query)
        else:
            return super(LectureListView, self).get_queryset().filter(profile__is_active=True)


class LectureStudentScripts(LoginRequiredMixin, TemplateView):

    def init_lecture_course_question_groups(self):
        lecture = self.request.user.lecturemodel
        filter_form = QuestionGroupFilterForm(course_queryset=self.request.user.lecturemodel.coursemodel_set,
                                              data=self.request.GET)
        filter_dict = dict(
                course__lecture=lecture,
                course__semester=self.request.user.generalsetting.semester,
                academic_year=self.request.user.generalsetting.academic_year,
            )

        if filter_form.is_valid():
            course = filter_form.cleaned_data.get("course")
            assessment_type = filter_form.cleaned_data.get("assessment_type")
            if course:
                filter_dict["course__id"] = course.id
            if assessment_type:
                filter_dict["questions_type"] = assessment_type

        scriptQ = self.request.GET.get("scriptQ")
        if scriptQ is not None and scriptQ.isidentifier():
            filter_dict["title__icontains"] = scriptQ
        try:
            self.question_group_queryset = QuestionGroup.objects.filter(
                **filter_dict
            ).exclude(status=QuestionGroupStatus.PREPARED).order_by("course")

        except AttributeError:
            raise get_not_allowed_render_response(request=self.request,
                                                  message="In preparing state only you can view, edit and delete the question")

    def get(self, request, *args, **kwargs):
        try:
            self.init_lecture_course_question_groups()
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)
        return super(LectureStudentScripts, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(LectureStudentScripts, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_group_queryset
        ctx["ACTION"] = self.request.GET.get("action")
        ctx["scriptQ"] = self.request.GET.get("scriptQ")
        ctx["filter_form"] = QuestionGroupFilterForm(course_queryset=self.request.user.lecturemodel.coursemodel_set,
                                                     data=self.request.GET)
        return ctx

    def get_template_names(self):
        template_name_1 = "lecture/scripts/all_scripts_lecture.html"
        template_name = "lecture/scripts/view.html"
        action = self.request.GET.get("action")
        if action == "listAllQS":
            return template_name_1
        else:
            return template_name


class QuizTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "lecture/scripts/quiz_view.html"

    def get_courses(self):
        lecture_model = self.request.user.lecturemodel
        return CourseModel.objects.filter(
            lecture=lecture_model,
            semester=lecture_model.profile.generalsetting.semester
        ).order_by("programme", "programme__department", )

    def get_context_data(self, **kwargs):
        ctx = super(QuizTemplateView, self).get_context_data(**kwargs)
        ctx["courses_set"] = self.get_courses()
        return ctx

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            return super(QuizTemplateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()


class OnGoingQuizTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "lecture/quiz/on_going_quiz.html"

    def get_quizzes_set(self):
        return QuestionGroup.objects.filter(
            course__lecture=self.request.user.lecturemodel,
            status=QuestionGroupStatus.CONDUCT,
            course__semester=self.request.user.generalsetting.semester
        )

    def get_context_data(self, **kwargs):
        ctx = super(OnGoingQuizTemplateView, self).get_context_data(**kwargs)
        ctx["quizzes"] = self.get_quizzes_set()
        return ctx

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            return super(OnGoingQuizTemplateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()


class DepartmentLecturesTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "lecture/hod/department_view.html"

    def init_instance(self):
        self.department_instance = get_object_or_404(
            Department,
            name=self.kwargs["department_name"]
        )
        
    def get(self, request, *args, **kwargs):
        self.init_instance()
        return super(DepartmentLecturesTemplateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DepartmentLecturesTemplateView, self).get_context_data(**kwargs)
        ctx["title"] = "Title"
        ctx["department"] = self.department_instance
        ctx["lecturers"] = self.get_lecturers()
        return ctx

    def get_lecturers(self):
        return self.department_instance.lecturemodel_set.all()


class QuestionGroupDetailView(LoginRequiredMixin, DetailView):
    template_name = "lecture/scripts/quiz_detailview.html"
    model = QuestionGroup

    def init_question_group_instance(self):
        self.question_group_instance = get_object_or_404(
            self.model,
            pk=self.kwargs.get("question_group_pk"),
            course__lecture=self.request.user.lecturemodel,
            course__semester=self.request.user.generalsetting.semester,
            course_id=self.kwargs.get("course_id"),
        )
        if self.question_group_instance.questions_type == QuestionTypeChoice.MULTICHOICE:
            self.question_solve = None
        elif self.question_group_instance.questions_type == QuestionTypeChoice.THEORY:
            try:
                scheme = self.question_group_instance.theorymarkingscheme
                self.question_solve = scheme.solution_set.count()
            except ObjectDoesNotExist:
                self.question_solve = None
        self.question_number = self.question_group_instance.question_set.count()

    def get_context_data(self, **kwargs):
        ctx = super(QuestionGroupDetailView, self).get_context_data(**kwargs)
        ctx["solved_q_num"] = self.question_solve
        ctx["questions_num"] = self.question_number
        ctx["student_script"] = self.get_scripts()
        ctx["has_published_alert"] = self.get_published_alert()
        ctx["script_marked"] = self.get_script_marked()
        return ctx

    def get_script_marked(self):
        marked = self.question_group_instance.get_marked_scripts().count()
        unmarked = self.question_group_instance.get_unmarked_scripts().count()

        if self.question_group_instance.is_all_scripts_marked():
            return "All marked"
        elif unmarked:
            return f'Marked ({marked}) and unmarked ({unmarked})'

        return f"None Marked ({unmarked})"

    def get_published_alert(self):
        affected_rows = self.request.session.get("publish_alert")

        def published_alert_counter():
            counter = self.request.session.get("published_alert_counter")
            if counter is None:
                self.request.session["published_alert_counter"] = 0
            elif counter >= 2:
                try:
                    del self.request.session["published_alert_counter"]
                    del self.request.session["publish_alert"]
                except KeyError:
                    pass
            else:
                self.request.session["published_alert_counter"] += 1

        if affected_rows is not None:
            published_alert_counter()
            return format_html("{} {} has been published successfully."
                               "<br><b>{} student scripts has been published, </b>"
                               " Students can see their {} scripts",
                               str(self.question_group_instance.course),
                               self.question_group_instance.get_title_display(),
                               affected_rows,
                               self.question_group_instance.get_title_display()
                               )
        elif affected_rows == 0:
            published_alert_counter()
            return format_html("{} {} scripts has been already published.",
                               str(self.question_group_instance.course),
                               self.question_group_instance.get_title_display())

    def get_scripts(self):
        if self.question_group_instance.questions_type == QuestionTypeChoice.MULTICHOICE:
            return self.question_group_instance.multichoicescripts_set.all()

        elif self.question_group_instance.questions_type == QuestionTypeChoice.THEORY:
            return self.question_group_instance.studenttheoryscript_set.all()

    def get_object(self, queryset=None):
        return self.question_group_instance

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture:
            self.init_question_group_instance()
            if self.question_group_instance.status != QuestionGroupStatus.PREPARED:
                return super(QuestionGroupDetailView, self).get(request, *args, **kwargs)
            else:
                return render(request, "assessment/status_not_allowed.html", {
                    "question_group_instance": self.question_group_instance,
                    "lecture_details": True,
                    "tip": get_status_tips(self.question_group_instance, QuestionGroupStatus)
                })

        else:
            return get_not_allowed_render_response(request)


class TheoryMarkingSchemeDetailView(LoginRequiredMixin, DetailView):
    template_name = "lecture/scheme/theory_marking_detail.html"

    def init_scheme_instance(self):
        lecture = self.request.user.lecturemodel
        self.question_group_instance = get_object_or_404(QuestionGroup,
                                                         pk=self.kwargs.get("question_group_pk"),
                                                         course_id=self.kwargs.get("course_id"),
                                                         course__lecture=lecture, )
        instance, created = TheoryMarkingScheme.objects.get_or_create(
            lecture=lecture,
            question_group=self.question_group_instance,
        )
        self.scheme_instance = instance

    def get_object(self, queryset=None):
        return self.scheme_instance

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture:
            self.init_scheme_instance()
            return super(TheoryMarkingSchemeDetailView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(TheoryMarkingSchemeDetailView, self).get_context_data(**kwargs)
        ctx["scheme_instance"] = self.scheme_instance
        ctx["is_questions_editable"] = self.question_group_instance.status == QuestionGroupStatus.PREPARED
        return ctx


class TheoryQuestionSolution(LoginRequiredMixin, CreateView):
    template_name = "lecture/scheme/solution_create_view.html"
    model = Solution
    form_class = LectureQuestionSolutionForm

    def init_instances(self):
        lecture = self.request.user.lecturemodel
        self.question_instance = get_object_or_404(
            Question,
            id=self.kwargs.get("question_id"),
            group__course_id=self.kwargs.get("course_id"),
            group__course__lecture=lecture,
            group_id=self.kwargs.get("question_group_id")
        )
        self.scheme_instance = get_object_or_404(
            TheoryMarkingScheme,
            pk=self.kwargs.get("scheme_pk"),
            question_group_id=self.kwargs.get("question_group_id")
        )

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            return super(TheoryQuestionSolution, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            return super(TheoryQuestionSolution, self).post(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def form_valid(self, form):
        form.instance.question = self.question_instance
        form.instance.scheme_id = self.scheme_instance.id
        return super(TheoryQuestionSolution, self).form_valid(form)

    def get_success_url(self):
        question_group = self.question_instance.group
        return reverse("lecture:theory_scheme_detail", kwargs={
            "course_id": question_group.course_id,
            "question_group_pk": question_group.pk
        })

    def get_context_data(self, **kwargs):
        ctx = super(TheoryQuestionSolution, self).get_context_data(**kwargs)
        ctx["question_instance"] = self.question_instance
        return ctx


class TheoryMarkingSchemeHomeTemplateView(LoginRequiredMixin, TemplateView):
    model = CourseModel
    template_name = "lecture/scheme/scheme_templateview.html"

    def get_queryset(self):
        return self.model.objects.filter(
            lecture=self.request.user.lecturemodel,
            semester=self.request.user.generalsetting.semester
        )

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_course_object()
            return super(TheoryMarkingSchemeHomeTemplateView, self).get(request, *args, **kwargs)
        elif self.request.user.is_staff:
            return get_not_allowed_render_response(request)
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(TheoryMarkingSchemeHomeTemplateView, self).get_context_data(**kwargs)
        if self.course_object:
            ctx["course"] = self.course_object
        else:
            ctx["courses_set"] = self.get_queryset()
        return ctx

    def init_course_object(self):
        course_code = self.request.GET.get("course_code")
        if course_code:
            self.course_object = get_object_or_404(
                self.model,
                lecture=self.request.user.lecturemodel,
                code=course_code
            )
        else:
            self.course_object = None

    def get_template_names(self):
        if self.course_object:
            return "lecture/scheme/quiz_list.html"
        else:
            return self.template_name


class TheoryQuestionSolutionUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "lecture/scheme/solution_create_view.html"
    model = Solution
    form_class = LectureQuestionSolutionForm

    def init_instances(self):
        lecture = self.request.user.lecturemodel
        self.question_instance = get_object_or_404(
            Question,
            id=self.kwargs.get("question_id"),
            group__course_id=self.kwargs.get("course_id"),
            group__course__lecture=lecture,
            group_id=self.kwargs.get("question_group_id")
        )

        self.solution_instance = get_object_or_404(
            Solution,
            question_id=self.question_instance,
            scheme_id=self.kwargs.get("scheme_id"),
            pk=self.kwargs.get("solution_pk"),

        )

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            return super(TheoryQuestionSolutionUpdateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            return super(TheoryQuestionSolutionUpdateView, self).post(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def get_success_url(self):
        question_group = self.question_instance.group
        return reverse("lecture:theory_scheme_detail", kwargs={
            "course_id": question_group.course_id,
            "question_group_pk": question_group.pk
        })

    def get_object(self, queryset=None):
        return self.solution_instance

    def get_context_data(self, **kwargs):
        ctx = super(TheoryQuestionSolutionUpdateView, self).get_context_data(**kwargs)
        ctx["question_instance"] = self.question_instance
        return ctx


class MarkTheoryScriptsDetailView(LoginRequiredMixin, DetailView):
    template_name = "lecture/scripts/mark/mark_detailview.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            if self.question_instance.status == QuestionGroupStatus.PUBLISHED:
                return render(request, "assessment/status_not_allowed.html", {
                    "question_group_instance": self.question_instance,
                    "reason": "Scripts are published no need to mark them again!",
                    "more": "Please you can not remark published scripts",
                    "published_icon": True,
                    "return_link": reverse("lecture:question_group_detail", kwargs={
                        "course_id": self.question_instance.course_id,
                        "question_group_pk": self.question_instance.pk,
                    }),
                })
                # "?open_page=1"
            return super(MarkTheoryScriptsDetailView, self).get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)

    def get_object(self, queryset=None):
        return self.question_instance

    def init_instances(self):
        lecture = self.request.user.lecturemodel
        self.question_instance = get_object_or_404(
            QuestionGroup,
            course__lecture=lecture,
            course__semester=self.request.user.generalsetting.semester,
            academic_year=self.request.user.generalsetting.academic_year,
            pk=self.kwargs.get("question_group_pk"),
            title=self.kwargs.get("question_group_title"),
            status__in=(QuestionGroupStatus.CONDUCTED, QuestionGroupStatus.MARKED, QuestionGroupStatus.PUBLISHED,
                        QuestionGroupStatus.CONDUCT)
        )
        self.student_scripts = self.question_instance.studenttheoryscript_set.all()
        self.marked_count = self.question_instance.get_marked_scripts().count()
        self.umarked = self.question_instance.get_unmarked_scripts().count()

        if self.question_instance.is_all_scripts_marked() and self.question_instance.status == \
                QuestionGroupStatus.CONDUCTED:
            self.question_instance.status = QuestionGroupStatus.MARKED
            self.question_instance.save()

    def get_context_data(self, **kwargs):
        ctx = super(MarkTheoryScriptsDetailView, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_instance

        if self.request.GET.get("filterOn") == 'on':
            self.filter_query()
            ctx["filter_on"] = True
        ctx["filter_form"] = FilterForms(self.request.GET)
        scriptSearch = self.request.GET.get("scriptSearch")
        if scriptSearch:
            self.student_scripts = self.student_scripts.filter(student__index_number__icontains=scriptSearch)

        ctx["student_scripts"] = self.student_scripts
        ctx["marked_count"] = self.marked_count
        ctx["unmarked_count"] = self.umarked
        ctx["scriptSearch"] = scriptSearch
        ctx["script_status"] = ScriptStatus
        return ctx

    def filter_query(self):
        from django.db.models import Q
        filter_form = FilterForms(self.request.GET)
        if filter_form.is_valid():
            marked = filter_form.cleaned_data["marked"]
            marking = filter_form.cleaned_data["marking"]
            submitted = filter_form.cleaned_data["submitted"]
            #pending = filter_form.cleaned_data["pending"]
            query = Q()
            try:
                if eval(marked):
                    query = Q(status=ScriptStatus.MARKED)

                if eval(marking):
                    query |= Q(status=ScriptStatus.MARKING)

                if eval(submitted):
                    query |= Q(status=ScriptStatus.SUBMITTED)

                # if eval(pending):
                #     query |= Q(status=ScriptStatus.PENDING)

                if query is not None:
                    self.student_scripts = self.student_scripts.filter(query)

            except (ValueError, TypeError):
                pass


class MarkScriptView(LoginRequiredMixin, View):
    template_name = "lecture/scripts/mark/mark_script.html"
    student_script_form_class = inlineformset_factory(parent_model=StudentTheoryScript, validate_min=True,
                                                      model=StudentTheoryAnswer,
                                                      form=StudentAnswerMarkForm,
                                                      extra=0,
                                                      validate_max=True,
                                                      can_delete=False,
                                                      can_order=False
                                                      )

    def get(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            ctx = self.get_context_data()
            ctx["student_script_formset"] = self.student_script_form_class(instance=self.student_script)
            return render(request, self.template_name, ctx)
        elif self.request.user.is_lecture:
            return get_not_allowed_render_response(request)
        else:
            return get_http_forbidden_response()

    def get_context_data(self):
        return {
            "lecture_scheme": self.marking_scheme,
            "quiz_title": self.marking_scheme.question_group.get_title_display(),
            "course_title_code": self.student_script.question_group.course,
            "student": self.student_script.student,
            "is_scroll_header": True
        }

    def post(self, request, *args, **kwargs):
        if self.request.user.is_lecture:
            self.init_instances()
            student_script_form = self.student_script_form_class(instance=self.student_script, data=request.POST)
            if student_script_form.is_valid():
                student_script_form.save()
                if self.complete_marking() and self.student_script.status == ScriptStatus.MARKING:
                    self.student_script.status = ScriptStatus.MARKED
                # question_group = self.marking_scheme.question_group
                self.student_script.total_score = self.student_script.score
                self.student_script.save()
                return redirect("lecture:mark_scripts", question_group_pk=self.marking_scheme.question_group.pk,
                                question_group_title=self.marking_scheme.question_group.title
                                )
            ctx = self.get_context_data()
            ctx["student_script_formset"] = student_script_form
            return render(request, self.template_name, ctx)
        else:
            return get_not_allowed_render_response(request)

    def init_instances(self):
        self.student_script = get_object_or_404(
            StudentTheoryScript,
            question_group_id=self.kwargs.get("question_group_id"),
            question_group__course__semester=self.request.user.generalsetting.semester,
            question_group__academic_year=self.request.user.generalsetting.academic_year,
            pk=self.kwargs.get("student_script_pk"),
            student__index_number=self.kwargs.get("student__index_number"),
        )

        self.marking_scheme = TheoryMarkingScheme.objects.get(
            pk=self.kwargs.get("scheme_pk"),
            lecture_id=self.request.user.lecturemodel.id,
            question_group_id=self.kwargs.get("question_group_id"),
        )

        if self.student_script.status == ScriptStatus.SUBMITTED:
            self.student_script.status = ScriptStatus.MARKING
            self.student_script.save()

    def complete_marking(self):
        return self.student_script.studenttheoryanswer_set.count() == \
               self.student_script.studenttheoryanswer_set.filter(score__isnull=False).count()

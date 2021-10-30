from django.shortcuts import render, get_object_or_404, redirect, reverse, resolve_url
from django.views.generic import View, DetailView, CreateView, UpdateView, DeleteView, ListView, TemplateView, \
    RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import is_safe_url
from .form import (MultiChoiceQuestionCreateForm, QuestionCreateForm, QuestionGroupCreateForm,
                   BaseOptionsFormSet, BaseOptionsInlineFormSet, AssessmentPreferenceCreateForm,
                   StudentMultiChoiceAnswerForm, StudentTheoryAnswerUpdateForm,
                    QuestionGroupUpdateForm,
                   )
from course.models import CourseModel
from .models import (MultiChoiceQuestion, Question, QuestionGroup, AssessmentPreference,
                     QuestionGroupStatus, MultiChoiceScripts, StudentMultiChoiceAnswer,
                     QuestionTypeChoice, StudentTheoryAnswer, StudentTheoryScript,
                     ScriptStatus
                     )
from django.forms import formset_factory, inlineformset_factory
from eAssessmentSystem.tool_utils import (admin_required_message, is_lecture, get_http_forbidden_response,
                                          get_status_tips, get_not_allowed_render_response,
                                        general_setting_not_init
                                          )
import string
from django.contrib.auth import get_user
from student.models import Student
from django.utils import timezone
from django.http import Http404
from django.core.paginator import Paginator
from urllib.parse import urlencode
import datetime
from setting.models import GeneralSetting
import random
from django.core.exceptions import ObjectDoesNotExist
from .duration_handler import AssessmentDurationHandler, AssessmentDueDateHandler


def check_view(view) -> bool:
    """
    Switch view from tabular to list display
    :param view: A string value of 0 or 1
    :return: True if view is 1 else False
    """
    if not view:
        return False
    view = str(view)
    if len(view) == 1 and view == "1":
        return True


def get_question_deadline_ended_render(question_group_instance, request, script=None):
    if question_group_instance.status == QuestionGroupStatus.CONDUCT and script:
        question_group_instance.status = QuestionGroupStatus.CONDUCTED
        question_group_instance.save()
    if script is not None:
        script.status = ScriptStatus.SUBMITTED
        script.save()
    return render(request, "assessment/time_up_view.html", {
        "question_group_instance": question_group_instance,
        "dead_line_ended": True,
    })


def get_status_not_allowed_reason(question_group):
    return "The %s status (%s) does not allowed the operation you want to perform on it." % \
           (question_group.get_title_display(), question_group.status)


class QuestionGroupCreateView(LoginRequiredMixin, CreateView):
    model = QuestionGroup
    form_class = QuestionGroupCreateForm
    template_name = "assessment/questionGroup_createview.html"

    def is_lecture_course_master(self):
        course = get_object_or_404(CourseModel,
                                   name=self.kwargs.get("courseName"),
                                   pk=self.kwargs.get("coursePK"),
                                   lecture=self.request.user.lecturemodel,
                                   semester=self.request.user.generalsetting.semester
                                   )
        self.course_instance = course
        return bool(course)

    def get(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master():
            return super(QuestionGroupCreateView, self).get(*args, **kwargs)
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            self.request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master():
            return super(QuestionGroupCreateView, self).post(*args, **kwargs)
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            self.request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_initial(self):
        initial = super(QuestionGroupCreateView, self).get_initial()
        course_name = self.kwargs.get("courseName")
        course_pk = self.kwargs.get("coursePK")
        initial["course"] = get_object_or_404(CourseModel, name=course_name, pk=course_pk)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super(QuestionGroupCreateView, self).get_context_data(**kwargs)
        ctx["course"] = self.get_initial().get("course")
        ctx["title"] = "Question Type"
        return ctx

    def get_success_url(self):
        if self.object.questions_type == "multichoice":
            return reverse("assessment:prepare_MCQ", kwargs=dict(QGT=self.object.title, QGPK=self.object.pk))
        else:
            return reverse("assessment:prepare_theory", kwargs={"QGT": self.object.title, "QGPK": self.object.pk})

    def form_invalid(self, form):
        form_ = form
        if "This course has a quiz with this title already." in form_.non_field_errors():
            form_.add_error("title", f"{self.course_instance.name.title()} has {str(self.request.POST.get('title'))} already. Please change the title")
        return super(QuestionGroupCreateView, self).form_invalid(form_)


class QuestionGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = QuestionGroup
    template_name = "assessment/questionGroup_createview.html"
    form_class = QuestionGroupUpdateForm

    def is_lecture_course_master(self):
        course = get_object_or_404(CourseModel,
                                   name=self.kwargs.get("courseName"),
                                   pk=self.kwargs.get("coursePK"),
                                   semester=self.request.user.generalsetting.semester,
                                   lecture=self.request.user.lecturemodel
                                   )
        return bool(course)

    def form_invalid(self, form):
        return super(QuestionGroupUpdateView, self).form_invalid(form)

    def get(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master() and self.get_question_group().status \
                == QuestionGroupStatus.PREPARED:
            return super(QuestionGroupUpdateView, self).get(*args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response("Please try again later!")
        else:
            return get_http_forbidden_response()

    def get_question_group(self):
        return get_object_or_404(QuestionGroup,
                                 pk=self.kwargs.get("pk"),
                                 title=self.kwargs.get("title"),
                                 course__semester=self.request.user.generalsetting.semester,
                                 academic_year=self.request.user.generalsetting.academic_year
                                 )

    def post(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master() and self.get_question_group().status \
                == QuestionGroupStatus.PREPARED:
            return super(QuestionGroupUpdateView, self).post(*args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with this.")
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(QuestionGroupUpdateView, self).get_context_data(**kwargs)
        ctx["title"] = "Update %s" % self.object
        return ctx


class AddOneMoreTheoryQuestion(LoginRequiredMixin, CreateView):
    template_name = "assessment/theory/add1theory.html"
    form_class = QuestionCreateForm
    model = Question

    def get(self, request, *args, **kwargs):
        self.init_instance()
        if request.user.is_lecture and self.question_group_instance.status == QuestionGroupStatus.PREPARED:
            return super(AddOneMoreTheoryQuestion, self).get(request, *args, **kwargs)
        elif self.question_group_instance.status != QuestionGroupStatus.PREPARED:
            return get_not_allowed_render_response(request, get_status_not_allowed_reason(self.question_group_instance))
        else:
            return get_not_allowed_render_response(request)

    def post(self, request, *args, **kwargs):
        self.init_instance()
        if request.user.is_lecture and self.question_group_instance.status == QuestionGroupStatus.PREPARED:
            return super(AddOneMoreTheoryQuestion, self).post(request, *args, **kwargs)
        elif self.question_group_instance.status != QuestionGroupStatus.PREPARED:
            return get_not_allowed_render_response(request, get_status_not_allowed_reason(self.question_group_instance))
        else:
            return get_not_allowed_render_response(request)

    def form_valid(self, form):
        form.instance.group = self.question_group_instance
        return super(AddOneMoreTheoryQuestion, self).form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url and is_safe_url(next_url, self.request.get_host()):
            return next_url
        else:
            return self.question_group_instance.get_absolute_url()

    def init_instance(self):
        self.question_group_instance = get_object_or_404(
            QuestionGroup,
            pk=self.kwargs.get("question_group_pk"),
            title=self.kwargs.get("question_group_title"),
            questions_type=self.kwargs.get("questions_type"),
            course__lecture__profile=self.request.user,
        )

    def get_context_data(self, **kwargs):
        ctx =super(AddOneMoreTheoryQuestion, self).get_context_data(**kwargs)
        ctx["title"] = "Add Question %s" % (self.question_group_instance.question_set.count() + 1)
        ctx["header"] = "%s %s" % (self.question_group_instance.course.name,
                                   self.question_group_instance.get_title_display().title())
        ctx["back_url"] = self.question_group_instance.get_absolute_url()
        return ctx


class CreateTheoryQuestion(LoginRequiredMixin, View):
    template_name = "assessment/prepareTheoryQuestions.html"
    question_formset = inlineformset_factory(parent_model=QuestionGroup, model=Question, form=QuestionCreateForm,
                                             can_delete=True, min_num=1, validate_min=True, validate_max=True, max_num=15)

    def get_question_group_instance(self):
        question_group_pk = self.kwargs.get("QGPK")
        question_group_title = self.kwargs.get("QGT")
        return get_object_or_404(QuestionGroup,
                                 title=question_group_title,
                                 pk=question_group_pk,
                                 course__semester=self.request.user.generalsetting.semester,
                                 academic_year=self.request.user.generalsetting.academic_year
                                 )

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture:
            question_group_instance = self.get_question_group_instance()
            ctx = {
                "questionFormSet": self.question_formset(instance=question_group_instance),
                "question_group": question_group_instance,
                "title": "Prepare %s Questions" % question_group_instance.get_title_display(),
            }
            return render(request, template_name="assessment/prepareTheoryQuestions.html", context=ctx)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture:
            question_group_instance = self.get_question_group_instance()
            question_form_set_instance = self.question_formset(data=request.POST, instance=question_group_instance)
            if question_form_set_instance.is_valid():
                question_form_set_instance.save(True)
                return redirect("assessment:question_grp_detail", courseName=question_group_instance.course.name,
                                title=question_group_instance.title, pk=question_group_instance.pk)
            else:
                ctx = {
                    "questionFormSet": question_form_set_instance,
                    "question_group": question_group_instance,
                    "title": "Prepare %s Questions" % question_group_instance.get_title_display(),
                }
                return render(request, template_name=self.template_name, context=ctx)
        else:
            return get_not_allowed_render_response(request)


class CreateMultipleChoiceQuestion(LoginRequiredMixin, View):
    objectives_formset = formset_factory(form=MultiChoiceQuestionCreateForm, min_num=2, can_delete=True,
                                         validate_min=True, max_num=6, validate_max=True,
                                         formset=BaseOptionsFormSet)
    question_form_class = QuestionCreateForm
    template_name = "assessment/prepareMCQ.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup,
                                                title=self.kwargs.get("QGT"),
                                                pk=self.kwargs.get("QGPK"),
                                                course__semester=self.request.user.generalsetting.semester,
                                                academic_year=self.request.user.generalsetting.academic_year,
                                                status=QuestionGroupStatus.PREPARED
                                                )

        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and user.is_active and self.is_lecture_course_master():
            ctx = self.get_context_data()
            ctx["multiChoiceQFormset"] = self.objectives_formset()
            ctx["questionForm"] = self.question_form_class()

            return render(request, template_name=self.template_name, context=ctx)
        request.session["admin_required"] = admin_required_message(user)
        return redirect("accounts:staff-login-page")

    def get_context_data(self):
        return {
            "title": "Prepare %s Multi-Choice Question" % self.question_group.get_title_display(),
            "question_group": self.question_group,
            "is_new": True,
            "question_number": self.question_group.question_set.count(),
            "table_view": check_view(self.request.GET.get("view"))
        }

    def post(self, request, *args, **kwargs):
        user = get_user(request)

        if user.is_lecture and user.is_active and self.is_lecture_course_master():
            question_form = self.question_form_class(request.POST)
            objectives = self.objectives_formset(request.POST)
            if question_form.is_valid() and objectives.is_valid():
                question_instance = question_form.save(False)
                question_instance.group = self.question_group
                question_instance.save()
                for objective in objectives:
                    if objective.is_valid():
                        obj_ins = objective.save(False)
                        obj_ins.question = question_instance
                        obj_ins.save()
                add_another = self.request.POST.get("add_save_and_another")
                if add_another:
                    return redirect(reverse("assessment:prepare_MCQ", kwargs={
                        "QGT": self.question_group.title,
                        "QGPK": self.question_group.pk
                    })
                                    )
                else:
                    return self.get_successful_url()
            else:
                ctx = self.get_context_data()
                ctx["multiChoiceQFormset"] = objectives
                ctx["questionForm"] = question_form
                return render(request, template_name=self.template_name, context=ctx)

    def get_successful_url(self):
        return redirect("assessment:question_grp_detail",
                        title=self.question_group.title,
                        pk=self.question_group.pk,
                        courseName=self.question_group.course.name)


class AssessmentQuestionGroupDetailView(LoginRequiredMixin, DetailView):
    model = QuestionGroup
    template_name = "assessment/question_detailview.html"

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(
                course__name=self.kwargs["courseName"],
                title=self.kwargs["title"],
                pk=self.kwargs["pk"],
                course__lecture=self.request.user.lecturemodel
            )
        except self.model.DoesNotExist:
            return self.model.objects.get(
                course__name=self.kwargs["courseName"],
                pk=self.kwargs["pk"],
                course__lecture=self.request.user.lecturemodel
            )

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_active and request.user.is_lecture:
                returns = super(AssessmentQuestionGroupDetailView, self).get(request, *args, **kwargs)
                if str(self.request.GET.get("fixquestionnum")) == "1":
                    self.fix_question()
                return returns
        except ObjectDoesNotExist:
            pass

        return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentQuestionGroupDetailView, self).get_context_data(**kwargs)
        ctx["questions"] = self.object.question_set.all()
        due_date = self.get_due_date()
        if due_date is not None:
            ctx["is_assessment_to_conduct_past"] = due_date < timezone.now()
        try:
            ctx["scheme_view"] = int(self.request.GET.get("scheme_view")) == 1
        except (ValueError, TypeError):
            pass
        ctx["assessment_to_conduct_past_msg"] = "Assessment due date(dead line) is in the past now please update the assessment preference."
        ctx["title"] = "%s - %s" % (self.object.get_title_display(), self.object.course)
        ctx["table_view"] = check_view(self.request.GET.get("view"))
        return ctx
    
    def get_due_date(self):
        if self.object.status in (QuestionGroupStatus.PREPARED, QuestionGroupStatus.CONDUCT):
            try:
                return self.object.preference.due_date
            except (AttributeError, ObjectDoesNotExist):
                return None
        return

    def fix_question(self):
        self.object.fix_question_numbers()


class EditTheoryQuestion(LoginRequiredMixin, UpdateView):
    """
    TODO check question status before proceeding to allow editing
    """
    model = Question
    template_name = "assessment/edit_question.html"
    form_class = QuestionCreateForm

    def is_lecture_course_master(self):
        self.question_ins = get_object_or_404(self.model,
                                              pk=self.kwargs.get("pk"),
                                              group__course__semester=self.request.user.generalsetting.semester,
                                              group__academic_year=self.request.user.generalsetting.academic_year
                                              )
        return self.question_ins.group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_active and user.is_lecture and self.is_lecture_course_master() and self.question_ins.group.status == QuestionGroupStatus.PREPARED:
            return super(EditTheoryQuestion, self).get(request=request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_not_allowed_render_response(request, message="We can not help you with that")
        else:
            return get_http_forbidden_response()

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_active and user.is_lecture and self.is_lecture_course_master() and self.question_ins.group.status == QuestionGroupStatus.PREPARED:
            return super(EditTheoryQuestion, self).post(request=request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")
        elif user and user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(EditTheoryQuestion, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_ins.group
        ctx["title"] = "Edit Theory Question"
        return ctx

    def get_success_url(self):
        group = self.object.group
        return reverse("assessment:question_grp_detail", kwargs={"courseName": group.course.name,
                                                                 "title": group.title,
                                                                 "pk": group.pk, }
                       )


class DeleteQuestion(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = "assessment/delete_question_view.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("group_title"),
                                                course=self.kwargs.get("coursePK"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            return super(DeleteQuestion, self).get(request, *args, **kwargs)
        elif self.is_lecture_course_master() and self.question_group.status != QuestionGroupStatus.PREPARED:
            return render(request, "assessment/status_not_allowed.html", {
                "reason": get_status_not_allowed_reason(self.question_group),
                "return_link": self.question_group.get_absolute_url(),
            })
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("group_title"),
                                                course=self.kwargs.get("coursePK"),
                                                academic_year=self.request.user.generalsetting.academic_year,
                                                course__semester=self.request.user.generalsetting.semester,
                                                )
        user = get_user(request)
        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            return super(DeleteQuestion, self).post(request, *args, **kwargs)

        elif self.question_group.status != QuestionGroupStatus.PREPARED:
            return render(request, "assessment/status_not_allowed.html", {
                "reason": get_status_not_allowed_reason(self.question_group),
                "return_link": self.question_group.get_absolute_url(),
            })
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_success_url(self):
        return self.question_group.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super(DeleteQuestion, self).get_context_data(**kwargs)
        ctx["title"] = "Delete Question"
        return ctx


class MultiChoiceQuestionEdit(LoginRequiredMixin, View):
    objectives_formset = inlineformset_factory(parent_model=Question, model=MultiChoiceQuestion,
                                               form=MultiChoiceQuestionCreateForm,
                                               min_num=2, can_delete=True, validate_min=True,
                                               formset=BaseOptionsInlineFormSet,
                                               max_num=6,
                                               validate_max=True,
                                               extra=1,

                                               )
    question_form_class = QuestionCreateForm
    template_name = "assessment/prepareMCQ.html"

    def is_lecture_course_master(self):
        self.question_instance = get_object_or_404(Question, pk=self.kwargs.get("questionPK"))
        self.course = self.question_instance.group.course
        return self.question_instance.group.course.lecture.profile == self.request.user and self.question_instance.group.title == self.kwargs.get(
            "group_title")

    def get_content_data(self):
        return {
            "title": "Edit %s %s " % (self.course, self.question_instance.group.get_title_display()),
            "question_group": self.question_instance.group,
            "question_number": self.kwargs.get("question_number"),
            "table_view": check_view(self.request.GET.get("view")),
            "question_number_on_edit": self.question_instance.question_number
        }

    def get(self, request, *args, **kwargs):
        user = get_user(request)

        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_instance.group.status == QuestionGroupStatus.PREPARED:
            ctx = self.get_content_data()
            ctx["multiChoiceQFormset"] = self.objectives_formset(instance=self.question_instance)
            ctx["questionForm"] = self.question_form_class(instance=self.question_instance)

            return render(request, template_name=self.template_name, context=ctx)
        elif self.is_lecture_course_master() and not self.question_instance.group.status != QuestionGroupStatus.PREPARED:
            return render(request, "assessment/status_not_allowed.html", {
                "reason": get_status_not_allowed_reason(self.question_instance.group),
                "return_link": self.question_instance.group.get_absolute_url(),
            })
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")

        return get_http_forbidden_response()

    def get_successful_url(self, question_group):
        return redirect("assessment:question_grp_detail",
                        title=question_group.title,
                        pk=question_group.pk,
                        courseName=question_group.course.name)

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_instance.group.status == QuestionGroupStatus.PREPARED:
            question_form = self.question_form_class(request.POST, instance=self.question_instance)
            multi_choice_question = self.objectives_formset(request.POST, instance=self.question_instance)

            if question_form.is_valid() and multi_choice_question.is_valid():
                question_form.save()
                multi_choice_question.save()
                return self.get_successful_url(self.question_instance.group)

            ctx = self.get_content_data()
            ctx["multiChoiceQFormset"] = multi_choice_question
            ctx["questionForm"] = question_form
            return render(request, self.template_name, ctx)
        else:
            return get_http_forbidden_response(message="We can not help you with that.")


class AssessmentView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/lecture_assessment_view.html"

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(user):
            try:
                return render(request, self.template_name, self.get_content_data())
            except ObjectDoesNotExist:
                return general_setting_not_init(request)
        elif request.user.is_admin:
            return get_not_allowed_render_response(request)
        return get_http_forbidden_response()

    def get_content_data(self):
        lecture = self.request.user.lecturemodel
        courses = CourseModel.objects.get_lecture_courses(lecture)
        return {
            "courses": courses,
            "lecture": lecture,
            "title": "Assessments",
        }


class PreparedQuestionsList(LoginRequiredMixin, ListView):
    model = QuestionGroup
    template_name = "assessment/prepared_questions_listview.html"

    def get_queryset(self):
        course_name_pk = (self.kwargs.get("course_name"), self.kwargs.get("course_pk"))
        course = get_object_or_404(CourseModel, name=course_name_pk[0], pk=course_name_pk[1],
                                   semester=self.request.user.generalsetting.semester)
        question_groups = self.model.objects.filter(course=course,
                                                    academic_year=self.request.user.generalsetting.academic_year
                                                    )
        return question_groups


class DeleteQuestionGroup(LoginRequiredMixin, DeleteView):
    model = QuestionGroup
    template_name = "assessment/delete_question_view.html"

    def is_lecture_course_master(self):
        self.course = get_object_or_404(CourseModel,
                                        pk=self.kwargs.get("coursePK"),
                                        name=self.kwargs.get("courseName"),
                                        semester=self.request.user.generalsetting.semester
                                        )
        return self.course.lecture.profile == self.request.user

    def get_question_group(self):
        return get_object_or_404(self.model,
                                 pk=self.kwargs.get("pk"),
                                 course_id=self.kwargs.get("coursePK"),
                                 course__name=self.kwargs.get("courseName"),
                                 academic_year=self.request.user.generalsetting.academic_year,
                                 course__semester=self.request.user.generalsetting.semester,
                                 )

    def get_object(self, queryset=None):
        return self.get_question_group()

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        question_group_instance = self.get_question_group()
        if is_lecture(
                user) and self.is_lecture_course_master() and question_group_instance.status == QuestionGroupStatus.PREPARED:
            return super(DeleteQuestionGroup, self).get(request, *args, **kwargs)
        elif is_lecture(user) and question_group_instance.status != QuestionGroupStatus.PREPARED:
            return render(request, "assessment/status_not_allowed.html",
                          {
                              "reason": get_status_not_allowed_reason(question_group_instance),
                              "return_link": question_group_instance.get_absolute_url(),
                          }
                          )
        elif is_lecture(user):
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        question_group_instance = self.get_question_group()
        if is_lecture(
                user) and self.is_lecture_course_master() and question_group_instance.status == QuestionGroupStatus.PREPARED:
            return super(DeleteQuestionGroup, self).post(request, *args, **kwargs)
        elif is_lecture(user) and question_group_instance.status != QuestionGroupStatus.PREPARED:
            return render(request, "assessment/status_not_allowed.html",
                          {
                              "reason": get_status_not_allowed_reason(question_group_instance),
                              "return_link": question_group_instance.get_absolute_url(),
                          }
                          )
        elif is_lecture(user):
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_success_url(self):
        return self.course.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super(DeleteQuestionGroup, self).get_context_data(**kwargs)
        try:
            ctx["title"] = "Delete %s %s" % (self.course.__str__(), self.object)
        except AttributeError as err:
            ctx["title"] = "Delete %s Question Group" % self.course.__str__()
        ctx["view"] = "qgd"

        return ctx


class ConductAssessment(LoginRequiredMixin, TemplateView):
    """Check if the assessment meet some requirement before proceeding to conducting the assessment"""
    template_name = "assessment/conductAssessment.html"
    MINIMUM_MINUTES = 10  # unit in minutes

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, pk=self.kwargs.get("question_group_pk"),
                                                title=self.kwargs.get("question_group_title"),
                                                academic_year=self.request.user.generalsetting.academic_year,
                                                course__semester=self.request.user.generalsetting.semester,
                                                course__lecture__profile=self.request.user
                                                )
        try:
            self.duration_instance = AssessmentDurationHandler(duration=self.question_group.preference.duration, script_timestamp=None)
        except AttributeError:
            self.duration_instance = AssessmentDurationHandler(None,None)

        try:
            self.due_datetime_instance = AssessmentDueDateHandler(self.question_group.preference.due_date)
        except AttributeError:
            self.due_datetime_instance = AssessmentDueDateHandler(None, None)

        return bool(self.question_group)

    def is_assessment_due(self):
        return self.due_datetime_instance.is_due

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        is_lecture_course_master = self.is_lecture_course_master()
        is_assessment_due = self.is_assessment_due()
        if user.is_lecture and is_lecture_course_master and self.question_group.status == QuestionGroupStatus.PREPARED and not is_assessment_due:
            if self.question_group.is_share_total_marks or self.question_group.questions_type == QuestionTypeChoice.MULTICHOICE:
                self.question_group.generate_marks()
            return super(ConductAssessment, self).get(request, *args, **kwargs)
        elif is_assessment_due:
            return get_question_deadline_ended_render(question_group_instance=self.question_group, request=request)
        elif user.is_staff:
            return get_not_allowed_render_response(request)
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(ConductAssessment, self).get_context_data(**kwargs)
        if self.question_group.status == QuestionGroupStatus.PREPARED:
            ctx["title"] = "Conduct"
            ctx["total_student"] = self.get_ready_student(self.question_group.course)
            ctx["calculated_total_marks"] = sum([q.max_mark or 0 for q in self.question_group.question_set.all()])
            ctx["student_level"] = self.question_group.course.level
            ctx["course"] = self.question_group.course
            try:
                due_date = self.question_group.preference.due_date
            except AttributeError:
                due_date = None
            if due_date:
                if self.duration_instance:
                    ctx["is_due_date_less_duration"] = self.due_datetime_instance < self.duration_instance
                    ctx["due_date_less_duration_msg"] = f"""Please the due date ({str(due_date)})
                                                        for this quiz is less than the actual duration 
                                                        ({self.duration_instance.hour}hrs :
                                                        {self.duration_instance.minute}mins :
                                                        {self.duration_instance.seconds}secs) set for the assessment.
                                                        Which makes the duration impossible to happen. 
                                                        If you would like to change it do so in the 
                                                        'change preference' link.
                                                        Time remaining is 
                                                        {str(self.due_datetime_instance.remaining_time())}""".replace("\n", "")
                 
        else:
            ctx["has_conducted"] = self.question_group.status != QuestionGroupStatus.PREPARED
        ctx["question_group"] = self.question_group
        return ctx

    def get_ready_student(self, course):
        return Student.objects.filter(programme__coursemodel=course, level=course.level).count()


class AssessmentPreferenceCreateView(LoginRequiredMixin, CreateView):
    model = AssessmentPreference
    form_class = AssessmentPreferenceCreateForm
    template_name = "assessment/assessment_preference.html"
    is_due_date_error = False

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"),
                                                course__lecture__profile=self.request.user,
                                                academic_year=self.request.user.generalsetting.academic_year,
                                                course__semester=self.request.user.generalsetting.semester,
                                                )
        return True if self.question_group else False

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        try:
            is_lecture_course_master = self.is_lecture_course_master()
            if user.is_lecture and is_lecture_course_master and self.question_group.status == QuestionGroupStatus.PREPARED:
                return super(AssessmentPreferenceCreateView, self).get(request, *args, **kwargs)
            elif self.question_group.status != QuestionGroupStatus.PREPARED:
                return render(request, template_name="assessment/status_not_allowed.html", context={
                    "reason": get_status_not_allowed_reason(self.question_group),
                })
        except Exception as err:
            if self.request.user.is_staff:
                return get_not_allowed_render_response(request)
            else:
                raise err

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            returns = super(AssessmentPreferenceCreateView, self).post(request, *args, **kwargs)
            self.question_group.preference = self.object
            self.question_group.save()
            return returns

        elif self.question_group.status != QuestionGroupStatus.PREPARED:
            return render(request, template_name="assessment/status_not_allowed.html", context={
                "reason": get_status_not_allowed_reason(self.question_group),
            })

        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentPreferenceCreateView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "%s %s Assessment Preference" % (
            self.question_group.course, self.question_group.get_title_display())
        ctx["title"] = ctx["cardHeader"]
        ctx["is_due_date_error"] = 1 if self.is_due_date_error else 0
        return ctx

    def get_success_url(self):
        return self.question_group.get_absolute_url()
    
    def form_invalid(self, form):
        if form.has_error("due_date"):
            self.is_due_date_error = True
        return super().form_invalid(form)


class ConductingAssessment(LoginRequiredMixin, TemplateView):
    template_name = "assessment/conducting_assessment.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(
            QuestionGroup,
            pk=self.kwargs.get("question_group_pk"),
            course_id=self.kwargs.get("course_pk"),
            course__lecture__profile_id=self.request.user.id,
        )
        generalsettings = self.request.user.generalsetting
        if self.question_group.questions_type == QuestionTypeChoice.MULTICHOICE:
            self.students_answer_scripts = MultiChoiceScripts.objects.filter(
                question_group_id=self.kwargs.get("question_group_pk"),
                course__name=self.kwargs.get("course_name"),
                course_id=self.kwargs.get("course_pk"),
                course__lecture=self.request.user.lecturemodel,
                question_group__academic_year=generalsettings.academic_year,
                course__semester=generalsettings.semester
            )
        elif self.question_group.questions_type == QuestionTypeChoice.THEORY:
            self.students_answer_scripts = StudentTheoryScript.objects.filter(
                question_group_id=self.kwargs.get("question_group_pk"),
                question_group__course__name=self.kwargs.get("course_name"),
                question_group__course_id=self.kwargs.get("course_pk"),
                question_group__course__lecture=self.request.user.lecturemodel,
                question_group__academic_year=generalsettings.academic_year,
                question_group__course__semester=generalsettings.semester
            )
        else:
            self.students_answer_scripts = None

        try:
            self.duration_instance = AssessmentDurationHandler(duration=self.question_group.preference.duration, script_timestamp=None)
        except AttributeError:
            self.duration_instance = AssessmentDurationHandler(None, None)

        try:
            self.due_datetime_instance = AssessmentDueDateHandler(self.question_group.preference.due_date)
        except AttributeError:
            self.due_datetime_instance = AssessmentDueDateHandler(None, None)

        return True

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        logic1 = self.is_lecture_course_master()

        logic2 = self.question_group.status in (QuestionGroupStatus.PREPARED, QuestionGroupStatus.CONDUCT)
        if logic1 and logic2:
            if self.question_group.theory_question_without_max_mark():
                self.question_group.generate_marks(force=True)
            self.question_group.status = QuestionGroupStatus.CONDUCT
            if not self.question_group.preference:
                preference = AssessmentPreference.objects.create()
                self.question_group.preference = preference
            self.question_group.save()
            return super(ConductingAssessment, self).get(request, *args, **kwargs)
        elif user.is_lecture and self.question_group.status not in (QuestionGroupStatus.PREPARED, QuestionGroupStatus.CONDUCT):
            return render(request, template_name="assessment/status_not_allowed.html", context={
                "reason": get_status_not_allowed_reason(self.question_group),
            })
        else:
            return get_not_allowed_render_response(request,
            )

    def get_context_data(self, **kwargs):
        ctx = super(ConductingAssessment, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_group
        ctx["student_total"] = self.get_student_total()
        ctx["student_script"] = self.students_answer_scripts
        ctx["end_time"] = self.question_group.preference.due_date
        ctx["student_finished"] = self.get_count_student_finished_the_work()
        ctx["time_left"] = self.due_datetime_instance.get_remaining_time
        ctx["start_time"] = self.question_group.updated
        return ctx

    def get_count_student_finished_the_work(self):
        if self.students_answer_scripts:
            return self.students_answer_scripts.filter(is_completed=True).count()

    def get_student_total(self):
        course = self.question_group.course
        self.students = Student.objects.filter(level=course.level, programme=course.programme, profile__is_active=True)
        return self.students.count()


class StudentCompletedPublishedAssessmentView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/student/assessment/published_script_page.html"

    @property
    def student(self):
        return self.request.user.student

    @property
    def course_instance(self):
        return get_object_or_404(
            CourseModel,
            code=self.kwargs.get("course_code"),
            name=self.kwargs.get("course_name")
        )

    def get_published_scripts(self):
        generallsettings = self.request.user.generalsetting
        theory = StudentTheoryScript.objects.filter(
            student=self.student,
            status__in=(ScriptStatus.PUBLISHED, ScriptStatus.SUBMITTED, ScriptStatus.MARKED),
            question_group__academic_year=generallsettings.academic_year,
            question_group__course__semester=generallsettings.semester,
            question_group__status__in=(QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.CONDUCTED,
                                        QuestionGroupStatus.CONDUCT, QuestionGroupStatus.MARKED,),
            question_group__course=self.course_instance,
        )
        mulitchoice =  MultiChoiceScripts.objects.filter(
            student=self.student,
            status__in=(ScriptStatus.PUBLISHED, ScriptStatus.SUBMITTED, ScriptStatus.MARKED),
            question_group__status__in=(QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.CONDUCTED,
                                        QuestionGroupStatus.CONDUCT, QuestionGroupStatus.MARKED,),
            question_group__academic_year=generallsettings.academic_year,
            course__semester=generallsettings.semester,
            course=self.course_instance
        )
        if self.searched_query:
            theory = theory.filter(question_group__title__icontains=self.searched_query)
            mulitchoice = mulitchoice.filter(question_group__title__icontains=self.searched_query)
        return theory, mulitchoice

    @property
    def searched_query(self):
        return self.request.GET.get("query")

    def get(self, request, *args, **kwargs):
        try:
            return super(StudentCompletedPublishedAssessmentView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(StudentCompletedPublishedAssessmentView, self).get_context_data(**kwargs)
        ctx["title"] = "Completed & Published"
        ctx["theory_script"], ctx["multichoice_script"] = self.get_published_scripts()
        ctx["back"] = self.get_back_url()
        ctx["sub_header"] = "%s Published Script and Completed Assessment" % self.course_instance
        ctx["query"] = self.searched_query
        return ctx

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url
        else:
            return reverse("assessment:student")


class StudentAssessmentView(LoginRequiredMixin, TemplateView):

    def init_student(self):
        self.student = self.request.user.student
        random.seed(self.student.id)
        page_id = list(string.ascii_letters + string.digits)
        random.shuffle(page_id)
        self.on_going_page_id = "".join(page_id)
        random.shuffle(page_id)
        self.new_assessment_page_id = "".join(page_id)
        random.shuffle(page_id)
        self.published_script_page_id = "".join(page_id)
        random.shuffle(page_id)
        self.assessment_records_script_page_id = "".join(page_id)

    def get(self, request, *args, **kwargs):
        try:
            self.init_student()
            if self.student and self.student.programme:
                return super(StudentAssessmentView, self).get(request, *args, **kwargs)
            else:
                return get_http_forbidden_response()
        except ObjectDoesNotExist:
            try:
                if self.request.user.student:
                    gen_set = GeneralSetting.objects.filter(user=self.request.user)
                    if gen_set.exists():
                        pass
                    else:
                        return general_setting_not_init(request)
            except ObjectDoesNotExist:
                pass
            return get_not_allowed_render_response(request)

    def get_question_groups(self):
        return QuestionGroup.objects.filter(course__level_id=self.student.level_id,
                                            course__programme=self.student.programme,
                                            status=QuestionGroupStatus.CONDUCT,
                                            course__semester=self.request.user.generalsetting.semester,
                                            academic_year=self.request.user.generalsetting.academic_year)

    def get_context_data(self, **kwargs):
        ctx = super(StudentAssessmentView, self).get_context_data(**kwargs)
        ctx["student"] = self.student
        ctx["title"] = "Student"
        ctx["on_going_page_id"] = self.on_going_page_id
        ctx["new_assessment_page_id"] = self.new_assessment_page_id
        ctx["assessment_records_page_id"] = self.assessment_records_script_page_id
        ctx["published_script_page_id"] = self.published_script_page_id

        page = self.request.GET.get("page")
        if page:
            if page == self.on_going_page_id:
                ctx["theory_script"], ctx["multichoice_script"] = self.get_ongoing_assessment()
                ctx["sub_header"] = "On going Assessment"
            elif page == self.new_assessment_page_id:
                ctx["new_assessment"] = self.get_new_assessment()
                ctx["sub_header"] = "New Assessment"
            elif page == self.published_script_page_id:
                ctx["sub_header"] = "Published Script and Completed Assessment"
                ctx["courses"] = self.assessment_courses()
            elif page == self.assessment_records_script_page_id:
                ctx["sub_header"] = "Assessment Records"
                ctx["courses"] = self.assessment_courses()
            else:
                ctx["home_page"] = True
        else:
            ctx["home_page"] = True
        return ctx

    def get_ongoing_assessment(self):
        generalsetting = self.request.user.generalsetting
        return StudentTheoryScript.objects.filter(
            student=self.student,
            question_group__course__semester=generalsetting.semester,
            question_group__academic_year=generalsetting.academic_year,
            question_group__status=QuestionGroupStatus.CONDUCT,
            status=ScriptStatus.ASSESSING,
        ), MultiChoiceScripts.objects.filter(
            student=self.student,
            course__semester=generalsetting.semester,
            question_group__academic_year=generalsetting.academic_year,
            question_group__status=QuestionGroupStatus.CONDUCT,
            status=ScriptStatus.ASSESSING
        )

    def get_new_assessment(self):
        general_setting = self.request.user.generalsetting
        student = self.request.user.student
        return QuestionGroup.objects.filter(
            course__semester=general_setting.semester,
            academic_year=general_setting.academic_year,
            status=QuestionGroupStatus.CONDUCT,
            course__programme_id=self.student.programme_id,
            course__level=student.level,
        ).exclude(studenttheoryscript__student__index_number=student.index_number)

    def assessment_courses(self):
        return CourseModel.objects.filter(
            level=self.student.level,
            programme__student=self.student,
            semester=self.request.user.generalsetting.semester,
            questiongroup__status__in=(QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.MARKED, QuestionGroupStatus.CONDUCTED,),

        ).distinct()

    @property
    def template_name(self):
        page = self.request.GET.get("page")
        if page == self.on_going_page_id:
            return "assessment/student/assessment/on_going_assessment.html"
        elif page == self.new_assessment_page_id:
            return "assessment/student/assessment/new_assessment_page.html"
        elif page == self.published_script_page_id:
            return "assessment/student/assessment/completed_publish_script_select_course.html"
        elif page == self.assessment_records_script_page_id:
            return "assessment/student/assessment/assessment_records_script_page.html"
        return "assessment/student/assessment/view.html"


class LectureStudentScriptTemplateView(LoginRequiredMixin, TemplateView):
    """
    Lecture previewing student script
    """
    template_name = "assessment/work/lecture_student_result.html"

    def get_student_scripts(self):
        questions_type = self.kwargs.get("questions_type")
        generallsettings = self.request.user.generalsetting
        if questions_type == QuestionTypeChoice.MULTICHOICE:
            return get_object_or_404(
                MultiChoiceScripts,
                student_id=self.kwargs.get("student_id"),
                course_id=self.kwargs.get("course_id"),
                course__lecture=self.request.user.lecturemodel,
                question_group_id=self.kwargs.get("question_group_id"),
                course__semester=generallsettings.semester,
                question_group__academic_year=generallsettings.academic_year
            )
        if questions_type == QuestionTypeChoice.THEORY:
            return get_object_or_404(
                StudentTheoryScript,
                student_id=self.kwargs.get("student_id"),
                question_group__course_id=self.kwargs.get("course_id"),
                question_group__course__lecture=self.request.user.lecturemodel,
                question_group_id=self.kwargs.get("question_group_id"),
                question_group__academic_year=generallsettings.academic_year,
                question_group__course__semester=generallsettings.semester,
            )

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture:
            return super(LectureStudentScriptTemplateView, self).get(request, *args, **kwargs)

        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        script = self.get_student_scripts()
        ctx = super(LectureStudentScriptTemplateView, self).get_context_data(**kwargs)
        ctx["title"] = "Student Script"
        ctx["student_script"] = script
        if script and isinstance(script, MultiChoiceScripts):
            ctx["course"] = script.course
            ctx["studentmultichoiceanswer_set"] = script.studentmultichoiceanswer_set.order_by(
                "question__question_number")
        elif script and isinstance(script, StudentTheoryScript):
            ctx["course"] = script.question_group.course
        return ctx


class GenerateQMarksRedirectQGroupRV(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.question_group_instance.get_absolute_url()

    def is_lecture_course_master(self):
        user = get_user(self.request)
        return user.is_lecture and user == self.question_group_instance.course.lecture.profile

    def get_question_group(self):
        self.question_group_instance = get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"),
                                                         pk=self.kwargs.get("QGPK"),
                                                         course__semester=self.request.user.generalsetting.semester,
                                                         academic_year=self.request.user.generalsetting.academic_year
                                                         )
        return self.question_group_instance

    def get(self, request, *args, **kwargs):
        question_group = self.get_question_group()
        if self.is_lecture_course_master() and question_group.status == QuestionGroupStatus.PREPARED:
            question_group.generate_marks()
            return super(GenerateQMarksRedirectQGroupRV, self).get(request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")
        else:
            return get_http_forbidden_response()


class AssessmentPreferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = AssessmentPreference
    form_class = AssessmentPreferenceCreateForm
    template_name = "assessment/assessment_preference.html"
    is_due_date_error = False

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"),
                                                course__semester=self.request.user.generalsetting.semester,
                                                academic_year=self.request.user.generalsetting.academic_year
                                                )
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and (
                self.question_group.status == QuestionGroupStatus.PREPARED or self.question_group.status == QuestionGroupStatus.CONDUCT):
            return super(AssessmentPreferenceUpdateView, self).get(request, *args, **kwargs)

        elif self.question_group.status != QuestionGroupStatus.PREPARED or self.question_group.status != QuestionGroupStatus.CONDUCT:
            return render(request, template_name="assessment/status_not_allowed.html", context={
                "reason": get_status_not_allowed_reason(self.question_group),
            })

        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and (
                self.question_group.status == QuestionGroupStatus.PREPARED or self.question_group.status == QuestionGroupStatus.CONDUCT):
            returns = super(AssessmentPreferenceUpdateView, self).post(request, *args, **kwargs)
            self.question_group.preference = self.object
            self.question_group.save()
            return returns
        elif self.question_group.status != QuestionGroupStatus.PREPARED or self.question_group.status != QuestionGroupStatus.CONDUCT:
            return render(request, template_name="assessment/status_not_allowed.html", context={
                "reason": get_status_not_allowed_reason(self.question_group),
            })
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentPreferenceUpdateView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "%s %s Assessment Preference Update" % (
            self.question_group.course, self.question_group.get_title_display())
        ctx["is_due_date_error"] = 1 if self.is_due_date_error else 0
        ctx["title"] = ctx["cardHeader"]
        return ctx

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url and is_safe_url(next_url, self.request.get_host()):
            return next_url
        return self.question_group.get_absolute_url()
    
    def form_invalid(self, form):
        if form.has_error("due_date"):
            self.is_due_date_error = True
        return super().form_invalid(form)


class StudentAssessingTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/student_assessing.html"

    def init_question_group(self):
        settings = self.request.user.generalsetting
        student = self.get_student()
        self.question_group_instance = get_object_or_404(QuestionGroup,
                                                         title=self.kwargs.get("QGT"),
                                                         pk=self.kwargs.get("QGPK"),
                                                         academic_year=settings.academic_year,
                                                         course__semester=settings.semester,
                                                         course__level=student.level,
                                                         course__programme=student.programme,
                                                         )
        QuestionGroup.objects.filter(


        )

    def get(self, request, *args, **kwargs):
        self.init_question_group()
        try:
            return super(StudentAssessingTemplateView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)

    def has_done_before(self):
        # Returns script urls if student has accessment or solve the quiz
        if self.question_group_instance.questions_type == QuestionTypeChoice.THEORY:
            try:
                script = StudentTheoryScript.objects.get(
                    student_id=self.get_student().id,
                    question_group_id=self.question_group_instance.id,
                    status__in=(ScriptStatus.SUBMITTED, ScriptStatus.MARKED, ScriptStatus.PUBLISHED)
                )
            except StudentTheoryScript.DoesNotExist:
                return
            else:
                return reverse("assessment:theory_exam_status", kwargs={
                    "script_pk": script.pk
                })

        else:
            return None

    def get_context_data(self, **kwargs):
        ctx = super(StudentAssessingTemplateView, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_group_instance
        ctx["q_preference"] = self.question_group_instance.preference
        ctx["course"] = self.question_group_instance.course
        ctx["student"] = self.get_student()
        current_year = timezone.now().date().year
        ctx["academic_year"] = current_year - 1, current_year
        ctx["script_url"] = self.has_done_before()
        return ctx

    def get_student(self):
        try:
            return self.request.user.student
        except ObjectDoesNotExist:
            return None


class ListLikeQueryset(list):
    def first(self):
        try:
            return self[0]
        except IndexError:
            return

    def last(self):
        try:
            return self[-1]
        except IndexError:
            return

    def all(self):
        return self

    def count(self, *args, **kwargs):
        return len(self)

    def exists(self):
        return self.first()


class MultiChoiceQuestionsExaminationView(LoginRequiredMixin, View):
    template_name = "assessment/multichoice_exam.html"
    student_multi_choice_answer_form_class = StudentMultiChoiceAnswerForm

    def is_student_qualified(self):
        self.student = self.request.user.student
        course = self.question_group_instance.course
        return self.student and self.student.level == course.level and self.student.programme == course.programme

    def get_paginator(self):
        if self.question_group_instance.preference.is_question_shuffle is True:
            random.seed(self.request.user.student.id)
            questions = ListLikeQueryset(self.question_group_instance.question_set.all())
            random.shuffle(questions)
            paginator = Paginator(object_list=questions, per_page=1)
        else:
            paginator = Paginator(object_list=self.question_group_instance.question_set.all(), per_page=1)
        page = self.request.GET.get("question")
        self.question_page = paginator.get_page(page)
        return paginator

    def get_question_instance(self):
        self.paginator = self.get_paginator()
        try:
            self.question_instance = self.question_page.object_list.first()
        except AttributeError:
            self.question_instance = self.question_page.object_list[0]

    def get_script(self):
        instance, created = MultiChoiceScripts.objects.get_or_create(
            student_id=self.student.id,
            course_id=self.question_group_instance.course_id,
            question_group_id=self.question_group_instance.id
        )
        self.script_instance = instance
        self.duration = AssessmentDurationHandler(duration=instance.question_group.preference.duration, script_timestamp=instance.timestamp)

        if self.duration:
            instance.time_remain = self.duration.remaining_time
        instance.save()
        return instance

    def init_required_instance(self):
        self.get_question_group()
        self.get_question_instance()
        if self.is_student_qualified():
            self.get_script()
            self.get_question_instance()

    def get_instance(self):
        instance, created = StudentMultiChoiceAnswer.objects.get_or_create(
            question_id=self.question_instance.id,
            script=self.get_script()
        )
        return instance

    def get(self, request, *args, **kwargs):
        self.init_required_instance()
        if self.is_student_qualified() and self.script_instance.is_completed is False and self.script_instance.is_canceled is False:
            if self.question_group_instance.preference.due_date and self.question_group_instance.preference.due_date <= timezone.now():
                return get_question_deadline_ended_render(self.question_group_instance, request=request,
                                                          script=self.script_instance)
            elif self.duration.is_time_up:
                self.__compute_score_and_complete_script__()
                return render(request, "assessment/time_up_view.html", {
                    "question_group_instance": self.question_group_instance
                })
            ctx = self.get_context_data()
            ctx["answer_form"] = self.student_multi_choice_answer_form_class(
                question_instance=self.question_instance, instance=self.get_instance(),
            )
            return render(request, template_name=self.template_name, context=ctx)

        elif self.script_instance:
            returns = self.get_script_response()
            if returns:
                return returns
        return get_http_forbidden_response()

    def get_script_response(self):
        ctx = {
            "reason": "Please, %s try again!\n" % self.student.get_name(),
            "tip": "If the problem persist and your not done with %s inform the lecture or supervisor or"
                   " any one who can help" % self.question_group_instance.get_title_display()
        }
        if self.script_instance.is_completed:
            ctx["is_completed"] = True
            ctx["question_group_instance"] = self.question_group_instance
            ctx["reason"] = f"You have already completed this Quiz. {str(self.question_group_instance.course)}" \
                            f" {self.question_group_instance.get_title_display()}"
            ctx["completed_url"] = reverse("assessment:result", kwargs={
                "student_id": self.student.id,
                "course_id": self.question_group_instance.course_id,
                "question_group_id": self.question_group_instance.id,
                "script_pk": self.script_instance.pk,
                "questions_type": self.question_group_instance.questions_type
            })
        elif self.script_instance.is_canceled is True:
            ctx["reason"] = "Sorry %s, your scripts is cancelled by the lecture %s" % (
                self.request.user.get_short_name(),
                self.question_group_instance.get_title_display()
            )
        return render(self.request, template_name="assessment/status_not_allowed.html", context=ctx)

    def __compute_score_and_complete_script__(self):
        self.script_instance.is_completed = True
        self.script_instance.status = ScriptStatus.MARKED
        self.script_instance.score_student()
        self.script_instance.save()

    def post(self, request, *args, **kwargs):
        self.init_required_instance()

        if self.question_instance and self.is_student_qualified():
            if self.script_instance.is_completed is False \
                    and self.script_instance.is_canceled is False and self.script_instance.has_paused is False:
                if self.question_group_instance.preference.due_date and self.question_group_instance.preference.due_date <= timezone.now():
                    return get_question_deadline_ended_render(self.question_group_instance, request,
                                                              self.script_instance)
                elif self.duration.is_time_up:
                    self.__compute_score_and_complete_script__()
                    return render(request, "assessment/time_up_view.html", {
                        "question_group_instance": self.question_group_instance
                    })
                submit_value = self.request.POST.get("submit")
                student_multi_choice_answer_form_class = self.student_multi_choice_answer_form_class(
                    question_instance=self.question_instance, instance=self.get_instance(), data=request.POST)
                if student_multi_choice_answer_form_class.is_valid():
                    student_multi_choice_answer_form_class.save(True)
                    if self.question_page.has_next() and not submit_value == "done":
                        url = resolve_url("assessment:MCQ_exam_start",
                                          course_code=self.question_group_instance.course.code,
                                          QGT=self.question_group_instance.title, QGPK=self.question_group_instance.pk
                                          ) + "?%s" % urlencode({"question": self.question_page.next_page_number()})
                        return redirect(url)

                    elif self.paginator.num_pages == self.question_page.number or submit_value == "done":
                        self.__compute_score_and_complete_script__()
                        return self.get_successful_url()
                    else:
                        url = resolve_url("assessment:MCQ_exam_start",
                                          course_code=self.question_group_instance.course.code,
                                          QGT=self.question_group_instance.title, QGPK=self.question_group_instance.pk
                                          ) + "?%s" % urlencode({"question": self.question_page.number()})
                        return redirect(url)

                else:
                    ctx = self.get_context_data()
                    ctx["answer_form"] = student_multi_choice_answer_form_class
                    return render(request, template_name=self.template_name, context=ctx)
            else:
                return self.get_script_response()
        else:
            return get_http_forbidden_response()

    def get_successful_url(self):
        return redirect("assessment:result",
                        student_id=self.script_instance.student_id,
                        course_id=self.script_instance.course_id,
                        question_group_id=self.script_instance.question_group_id,
                        script_pk=self.script_instance.pk,
                        questions_type=self.script_instance.question_group.questions_type)

    def get_context_data(self):
        question_group_instance = self.question_group_instance

        return {

            "title": "%s start" % question_group_instance.get_title_display(),
            "question": self.question_instance,
            "today": timezone.now(),
            "duration": self.duration,
            "used_time": self.duration.used_time,
            "question_page": self.question_page,
            "start_timestamp": self.duration.script_timestamp,
            "end_time": self.duration.end_time,
            "due_date": question_group_instance.preference.due_date,
            "student": self.student,
            "is_script_hold": self.script_instance.has_paused,
        }

    def get_question_group(self):
        self.question_group_instance = get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"),
                                                         pk=self.kwargs.get("QGPK"),
                                                         course__code=self.kwargs.get("course_code"))
        # return self.question_group_instance


class QuestionResultDetailTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/result_detail.html"

    def is_student(self):
        try:
            return get_user(self.request).student
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        if self.is_student():
            self.init_student_script()
            if self.student_script_instance.status == ScriptStatus.PUBLISHED:
                # if isinstance(self.student_script_instance, MultiChoiceScripts):
                #     self.student_script_instance.score_student()
                return super(QuestionResultDetailTemplateView, self).get(request, *args, **kwargs)
            else:
                return render(request, "assessment/status_not_allowed.html",
                              {
                                  "reason": "%s - %s is not published yet!" % (self.course_instance,
                                                                               self.student_script_instance.question_group.get_title_display()),
                                  "published_icon": True,
                                  "more": "The lecture %s has not published the script" % self.course_instance.lecture,
                                  "return_link": reverse("assessment:student"),
                              })
        elif self.request.user:
            return render(request, "assessment/status_not_allowed.html", {
                "reason": "Only Students are allowed to access this page",
                "tip": "If your are a student see authorities"
            })
        else:
            return get_http_forbidden_response()

    def init_student_script(self):
        generalsetting = self.request.user.generalsetting
        try:
            questions_type = self.kwargs.get("questions_type")
            if questions_type == QuestionTypeChoice.MULTICHOICE:
                self.student_script_instance = MultiChoiceScripts.objects.get(
                                                                 student_id=self.request.user.student.id,
                                                                 course_id=self.kwargs.get("course_id"),
                                                                 question_group_id=self.kwargs.get("question_group_id"),
                                                                 question_group__academic_year=generalsetting.academic_year,
                                                                 course__semester=generalsetting.semester,
                                                                 question_group__questions_type=self.kwargs.get("questions_type")
                                                                 )
                self.course_instance = self.student_script_instance.course

            elif questions_type == QuestionTypeChoice.THEORY:
                self.student_script_instance = StudentTheoryScript.objects.get(
                    student_id=self.request.user.student.id,
                    question_group__course_id=self.kwargs.get("course_id"),
                    question_group_id=self.kwargs.get("question_group_id"),
                    question_group__academic_year=generalsetting.academic_year,
                    question_group__course__semester=generalsetting.semester,
                    question_group__questions_type=self.kwargs.get("questions_type")
                )
                self.course_instance = self.student_script_instance.question_group.course
        except (StudentTheoryScript.DoesNotExist, MultiChoiceScripts.DoesNotExist):
            raise Http404("Page Not Found")

    def get_context_data(self, **kwargs):
        ctx = super(QuestionResultDetailTemplateView, self).get_context_data(**kwargs)
        ctx["student_script"] = self.student_script_instance
        ctx["student"] = self.request.user.student
        ctx["question_group"] = self.student_script_instance.question_group
        total_question_num = self.student_script_instance.question_group.question_set.count()
        answered = self.student_script_instance.get_answered_question_queryset().count()
        ctx["answered_option"] = answered
        ctx["un_answered_option"] = total_question_num - answered
        ctx["total_questions_num"] = total_question_num
        ctx["score"] = self.get_score()
        wrong_answers_num = self.student_script_instance.get_wrong_answers_count()
        ctx["correct_answers_num"] = total_question_num - wrong_answers_num
        ctx["wrong_answers_num"] = wrong_answers_num
        ctx["course"] = self.course_instance
        ctx["is_mulichoice"] = isinstance(self.student_script_instance, MultiChoiceScripts)
        ctx["title"] = f"{self.course_instance.name} {self.student_script_instance.question_group.get_title_display()} Script- {self.student_script_instance.student}"
        return ctx

    def get_score(self):
        if isinstance(self.student_script_instance, MultiChoiceScripts):
            return self.student_script_instance.get_selected_option__is_answer_option_sum()
        elif isinstance(self.student_script_instance, StudentTheoryScript):
            return self.student_script_instance.total_score


class QuestionResultTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/resultview.html"

    def is_student_script(self):
        student = self.request.user.student
        return student == self.get_student_script().student

    def get(self, request, *args, **kwargs):
        try:
            if self.is_student_script():
                try:
                    self.student_script_instance.score_student()
                except AttributeError:
                    # We can not mark and score theory quiz
                    pass
                return super(QuestionResultTemplateView, self).get(request, *args, **kwargs)
            else:
                return get_http_forbidden_response()
        except ObjectDoesNotExist as err:
            return get_not_allowed_render_response(request)

    def get_student_script(self):
        try:
            self.student_script_instance = StudentTheoryScript.objects.get(
                student_id=self.request.user.student.id,
                question_group__course_id=self.kwargs.get("course_id"),
                question_group_id=self.kwargs.get("question_group_id"),
                question_group__course__semester=self.request.user.generalsetting.semester,
                question_group__academic_year=self.request.user.generalsetting.academic_year,
                pk=self.kwargs.get("script_pk"),
                question_group__questions_type=self.kwargs.get("questions_type"),
            )
        except StudentTheoryScript.DoesNotExist:
            self.student_script_instance = MultiChoiceScripts.objects.get(
                student_id=self.request.user.student.id,
                course_id=self.kwargs["course_id"],
                question_group_id=self.kwargs["question_group_id"],
                question_group__academic_year=self.request.user.generalsetting.academic_year,
                course__semester=self.request.user.generalsetting.semester,
                pk=self.kwargs.get("script_pk"),
                question_group__questions_type=self.kwargs.get("questions_type"),
            )
        except MultiChoiceScripts.DoesNotExist:
            raise Http404("Page Not found")

        return self.student_script_instance

    def get_context_data(self, **kwargs):
        ctx = super(QuestionResultTemplateView, self).get_context_data(**kwargs)
        ctx["student_script"] = self.student_script_instance
        total_question_num = self.student_script_instance.question_group.question_set.count()
        ctx["total_questions_num"] = total_question_num
        ctx["score"] = self.student_script_instance.score
        ctx["back"] = self.get_back_url()
        ctx["is_published"] = self.student_script_instance.status == ScriptStatus.PUBLISHED
        ctx["total_marks"] = self.student_script_instance.question_group.total_marks
        if isinstance(self.student_script_instance, MultiChoiceScripts):
            # answered = self.student_script_instance.get_answered_question_queryset().count()
            ctx["total_correct_ans_num"] = total_question_num - self.student_script_instance.get_wrong_answers_count()
            ctx["avg_mark"] = self.student_script_instance.question_group.total_marks / 2

        elif isinstance(self.student_script_instance, StudentTheoryScript):
            avg_score = self.student_script_instance.question_group.total_marks / 2
            try:
                ctx["pass_avg"] = avg_score <= self.student_script_instance.total_score
            except TypeError:
                ctx["pass_avg"] = None
            try:
                ctx["pass_better"] = (avg_score + (avg_score/2)) <= self.student_script_instance.total_score
            except TypeError:
                ctx["pass_better"] = None
        return ctx

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url


class QuestionsPreviewTemplateView(LoginRequiredMixin, TemplateView):
    """
        Lecture preview Questions while Assessing is on going.
    """
    template_name = "assessment/preview_questions.html"

    def is_lecture_course_master(self):
        """
        Check if the lecture can open this page by checking if the question course lecture is this lecture
        :return: True or False
        """

        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        """
        check authorization.
        if the question has no preference create on for it.
        :param request:
        :param args:
        :param kwargs:
        :return: rendered page
        """
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and self.question_group.status != QuestionGroupStatus.PREPARED:
            # self.question_group.status = "conduct"
            # if not self.question_group.preference:
            #     preference = AssessmentPreference.objects.create(
            #         due_date=timezone.now(),
            #     )
            #     self.question_group.preference = preference
            # self.question_group.save()
            return super(QuestionsPreviewTemplateView, self).get(request, *args, **kwargs)

        # TODO return QuestionGroup Status Not Allow page if the Question Status failure to validate
        elif self.is_lecture_course_master():
            return render(request, "assessment/status_not_allowed.html",
                          {
                              "reason": get_status_not_allowed_reason(self.question_group)
                          })
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(QuestionsPreviewTemplateView, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_group
        ctx["total_questions_num"] = self.question_group.question_set.count()
        ctx["all_questions"] = self.question_group.question_set.all()
        return ctx


class TheoryQuestionsExaminationView(LoginRequiredMixin, View):
    # student_answer_model = StudentTheoryAnswer
    template = "assessment/theory/examview.html"

    def get_script(self):
        instance, created = StudentTheoryScript.objects.get_or_create(
            student=self.student,
            question_group=self.question_group_instance,
            is_completed=False,
            status=ScriptStatus.ASSESSING
        )
        self.script_instance = instance

        return instance

    def has_question_group(self):
        try:
            self.student = self.request.user.student
            self.question_group_instance = get_object_or_404(QuestionGroup,
                                                             title=self.kwargs.get("question_group_title"),
                                                             pk=self.kwargs.get("question_group_id"),
                                                             course__level=self.student.level,
                                                             course__programme=self.student.programme,
                                                             course__semester=self.request.user.generalsetting.semester,
                                                             status=QuestionGroupStatus.CONDUCT,
                                                             )

            return True
        except Exception as err:
            return False

    def is_semester_eq_course_semester(self):
        """

        Check the semester the settings in the user profile and in course object to if they are equal
        :return:  True or False
        """
        course = self.question_group_instance.course
        try:
            # Try if user has general_setting object
            return self.request.user.generalsetting.semester == course.semester
        except ObjectDoesNotExist:
            # If Not create new settings for the user and return. Since the semester validate after creation
            general_settings, created = GeneralSetting.objects.get_or_create(user=self.request.user)
            if created:
                general_settings.semester = course.semester
                general_settings.save()
                return True
            else:
                # Compare Semesters
                return general_settings.semester == course.semester

    def process(self):
        # Initialise class instances
        self.get_script()
        self.duration = AssessmentDurationHandler(duration=self.question_group_instance.preference.duration, script_timestamp=self.script_instance.timestamp)
        self.assessment_due_date = AssessmentDueDateHandler(self.question_group_instance.preference.due_date)

    def get_not_semester_template(self):
        """

        :return: I f semester failed to validate render and return a decent view
        """
        course = self.question_group_instance.course
        gen_set = self.request.user.generalsetting
        return render(self.request, template_name="assessment/status_not_allowed.html", context={
            "reason": f"""Sorry {self.student.get_name()}, this {str(course)} assessment.
            Is registered only for {course.get_semester_display()} Only.""",
            "tip": f"""Try changing your Semester in the settings to {course.get_semester_display()}
                  Else consult the Course master: {str(course.lecture).upper()}.""",
            "more": f"""
            Your Semester is set to: {gen_set.get_semester_display()}.
            Course Semester is set to: {course.get_semester_display()}
            """
        })

    def get(self, request, *args, **kwargs):
        if self.has_question_group():
            self.process()
            if not (self.assessment_due_date.is_due or self.duration.is_time_up):
                ctx = self.get_content_data()
                return render(request, self.template, ctx)
            if self.assessment_due_date.is_due:
                return get_question_deadline_ended_render(self.question_group_instance, request=request,
                                                          script=self.script_instance)
        return get_not_allowed_render_response(request)

    def get_question_status_not_allowed(self):
        return render(self.request, "assessment/status_not_allowed.html",
                      context={"question_group_instance": self.question_group_instance}
                      )

    def get_script_status_not_allowed(self):
        return render(self.request, "assessment/status_not_allowed.html", context={
            "script_instance": self.script_instance,
            "return_link": reverse("assessment:student")

        })

    def can_delete_alert(self):
        try:
            saved_mins = self.request.session["answer_saved_mins"]
            if saved_mins >= 2:
                del self.request.session["answer_saved_mins"]
                del self.request.session["answer_saved"]
            else:
                self.request.session["answer_saved_mins"] += 1
        except KeyError:
            pass

    def get_content_data(self):
        self.can_delete_alert()
        now = timezone.now()
        return {
            "question_group_instance": self.question_group_instance,
            "used_time": self.duration.used_time,
            "used_time_str": str(self.duration.used_time),
            "script_pk": self.script_instance.pk,
            "answer_saved": self.request.session.get("answer_saved"),
            "answer_saved_datetime": self.request.session.get("answer_saved_datetime"),
            "today": datetime.datetime(now.year, month=now.month, day=now.day, hour=self.duration.used_time.hour,
                                       minute=self.duration.used_time.minute, second=self.duration.used_time.second

                                       ),
        }

    def post(self, request, *args, **kwargs):
        if self.has_question_group():
            self.process()
            if not (self.assessment_due_date.is_due or self.duration.is_time_up):
                ctx = self.get_content_data()
                btn_clicked = self.request.POST.get("button")
                if not btn_clicked == "home":
                    try:
                        return self.get_submission_urls()[btn_clicked]
                    except KeyError:
                        pass
                return render(request, self.template, ctx)
                # return self.get_not_semester_template()
            elif self.assessment_due_date.is_due:
                return get_question_deadline_ended_render(self.question_group_instance, request=request,
                                                          script=self.script_instance)
            elif self.question_group_instance.status != QuestionGroupStatus.CONDUCT:
                return self.get_question_status_not_allowed()
            elif self.question_group_instance.status != QuestionGroupStatus.CONDUCT:
                return self.get_question_status_not_allowed()
            elif self.script_instance.is_completed or self.script_instance.status != ScriptStatus.ASSESSING:
                return self.get_script_status_not_allowed()

        return get_not_allowed_render_response(request)

    def get_submission_urls(self):
        ctx = {
            "script": self.script_instance,
            "title": f"{self.student.get_name()} - {self.script_instance.question_group.get_title_display()}",
            "script_pk":self.script_instance.pk,
        }
        return {
            "preview": render(self.request, "assessment/theory/preview_ans.html", ctx),
            "submit": render(self.request, "assessment/theory/submit_script.html", ctx),
            "done": redirect("assessment:theory_exam_status", script_pk=self.script_instance.pk)
        }


class TheoryQuestionAnswerView(LoginRequiredMixin, View):
    student_script_model = StudentTheoryScript
    template_name = "assessment/theory/examAnswerView.html"
    model = StudentTheoryAnswer
    form_class = StudentTheoryAnswerUpdateForm

    def init_script_instances(self):
        self.script = get_object_or_404(StudentTheoryScript,
                                        question_group__title=self.kwargs.get("question_group_title"),
                                        question_group_id=self.kwargs.get("question_group_id"),
                                        pk=self.kwargs.get("script_pk"),
                                        student=self.request.user.student
                                        )
        self.question_instance = self.script.question_group.question_set.get(pk=self.kwargs.get("question_pk"))

    def init_answer_instance(self):
        instance, created = self.model.objects.get_or_create(
            script=self.script,
            question=self.question_instance,
        )
        self.theory_answer_instance = instance
        self.duration = AssessmentDurationHandler(self.question_instance.group.preference.duration, self.script.timestamp)
        self.assessment_due_date = AssessmentDueDateHandler(self.question_instance.group.preference.due_date)

    def process(self):
        self.init_script_instances()
        self.init_answer_instance()

    def get_script_status_not_allowed(self):
        return render(self.request, "assessment/status_not_allowed.html", context={
            "script_instance": self.script,
            "return_link": reverse("assessment:student"),
            "face_icon": True
        })

    def get_context_data(self):
        return {
            "question_instance": self.question_instance,
            "answer_saved": self.request.session.get("answer_saved"),
            "answer_saved_datetime": self.request.session.get("answer_saved_datetime"),
            "duration": self.duration.duration,
            "used_time": self.duration.used_time,
            "used_time_str": str(self.duration.used_time),
            "title": f"{str(self.script.question_group.course)} {self.question_instance.group.get_title_display()} assessing",
            "back_url": self.get_back_url()
        }

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url is not None and is_safe_url(back_url, self.request.get_host()):
            return back_url

    def is_duration_and_due_date_normal(self):
        """
        check if the assessment due date is up and the use has duration left
        :return:
        """
        return not (self.assessment_due_date.is_due or self.duration.is_time_up)

    def get_question_status_not_allowed(self):
        return render(self.request, "assessment/status_not_allowed.html",
                      context={"question_group_instance": self.question_instance.group})

    def get(self, request, *args, **kwargs):
        try:
            self.process()
            if request.user.student and self.question_instance.group.status == QuestionGroupStatus.CONDUCT \
                    and self.script.is_completed is False:

                if self.is_duration_and_due_date_normal():
                    ctx = self.get_context_data()
                    ctx["answer_form"] = self.form_class(instance=self.theory_answer_instance)
                    return render(request, self.template_name, ctx)
                elif self.is_duration_and_due_date_normal() is False:
                    return self.get_render_time_up()

            elif self.script.is_completed is True:
                return self.get_render_is_completed()

            elif self.question_instance.group.status != QuestionGroupStatus.CONDUCT:
                return self.get_question_status_not_allowed()

            elif self.script.is_completed:
                return self.get_script_status_not_allowed()

            return get_http_forbidden_response()
        except AttributeError as err:
            raise err
            # return get_http_forbidden_response()

    def get_render_is_completed(self):
        return render(self.request, "assessment/status_not_allowed.html",
                      {
                          "reason": "You script (answer sheet) has been submitted."
                                    " You can not solve any question on this Quiz again.",
                          "tip": "if you do not submitted by yourself, see authorities",
                          "script_icon": True,
                          "return_link": reverse("assessment:student")
                      })

    def get_render_time_up(self):
        return render(self.request, "assessment/time_up_view.html",
                      {
                          "script_instance": self.script
                      })

    def post(self, request, *args, **kwargs):
        try:
            self.process()
            if request.user.student and self.question_instance.group.status == QuestionGroupStatus.CONDUCT \
                    and self.script.is_completed is False and self.script.status == ScriptStatus.ASSESSING:

                if self.is_duration_and_due_date_normal():
                    ctx = self.get_context_data()
                    answer_form = self.form_class(instance=self.theory_answer_instance, data=request.POST)
                    if answer_form.is_valid():
                        answer_form.save(True)
                        request.session["answer_saved"] = True
                        request.session["answer_saved_mins"] = 0
                        return redirect("assessment:theory_exam_start",
                                        question_group_title=self.script.question_group.title,
                                        question_group_id=self.script.question_group.id,
                                        semester=self.script.question_group.course.semester,
                                        )
                    else:
                        ctx["answer_form"] = answer_form
                        return render(request, self.template_name, ctx)
                else:
                    return self.get_render_time_up()
            elif self.script.status != ScriptStatus.ASSESSING:
                return self.get_script_status_not_allowed()
            elif self.script.is_completed is True:
                return self.get_render_is_completed()
            elif not (self.question_instance.group.status == QuestionGroupStatus.CONDUCT):
                return self.get_question_status_not_allowed()
        except ObjectDoesNotExist:
            pass
        return get_not_allowed_render_response(request)


class TheoryScriptStatusTemplateView(LoginRequiredMixin, TemplateView):

    def init_script_instance(self):
        self.script_instance = get_object_or_404(
            StudentTheoryScript,
            pk=self.kwargs.get("script_pk"),
            student_id=self.request.user.student.id
        )

    def get(self, request, *args, **kwargs):
        self.init_script_instance()
        if self.script_instance.status == ScriptStatus.ASSESSING:
            self.script_instance.status = ScriptStatus.SUBMITTED
            self.script_instance.is_completed = True
            self.script_instance.submitted_at = timezone.now()
            self.script_instance.save()

        return super(TheoryScriptStatusTemplateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TheoryScriptStatusTemplateView, self).get_context_data(**kwargs)
        ctx["script"] = self.script_instance
        ctx["course"] = self.script_instance.question_group.course
        ctx["script_status"] = True if self.request.GET.get("preview") else False
        return ctx

    def get_template_names(self):
        preview = self.request.GET.get("preview")
        back = self.request.GET.get("back")
        if preview == "preview_student_stu_script" and not back == 1:
            return "assessment/theory/preview_ans.html"
        else:
            return "assessment/theory/script_status.html"


class StopAllWorkTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/work/stop_all.html"

    def init_question_group(self):
        self.question_group_instance = get_object_or_404(
            QuestionGroup,
            pk=self.kwargs.get("question_group_pk"),
            course__lecture=self.request.user.lecturemodel,
            course_id=self.kwargs.get("course_id"),
            title=self.kwargs.get("question_group_title"),
        )

    def get(self, request, *args, **kwargs):
        self.init_question_group()
        if self.request.user.is_lecture and self.question_group_instance.status == QuestionGroupStatus.CONDUCT:
            if self.request.GET.get("confirm") == "yes":
                self.question_group_instance.status = QuestionGroupStatus.CONDUCTED
                self.question_group_instance.save()
                return self.get_confirm_redirect()
            return super(StopAllWorkTemplateView, self).get(request, *args, **kwargs)
        elif self.question_group_instance.status != QuestionGroupStatus.CONDUCT and self.request.user.is_lecture:
            return render(request, "assessment/status_not_allowed.html",
                          {"question_group_instance": self.question_group_instance,
                           "reason": f"{self.question_group_instance.get_title_display()} status  "
                                     f"({self.question_group_instance.get_status_display()}) does not allow this operation",
                           "tip": get_status_tips(self.question_group_instance, QuestionGroupStatus)
                           },
                          )
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(StopAllWorkTemplateView, self).get_context_data(**kwargs)
        ctx["question_group_instance"] = self.question_group_instance
        return ctx

    def get_confirm_redirect(self):
        return redirect("lecture:question_group_detail", question_group_pk=self.question_group_instance.pk,
                        course_id=self.question_group_instance.course_id)

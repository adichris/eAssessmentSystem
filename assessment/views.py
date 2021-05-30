from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, DetailView, CreateView, UpdateView, DeleteView, ListView, TemplateView, \
    RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import (MultiChoiceQuestionCreateForm, QuestionCreateForm, QuestionGroupCreateForm,
                   BaseOptionsFormSet, BaseOptionsInlineFormSet, AssessmentPreferenceCreateForm,
                    StudentMultiChoiceAnswerForm,
                   )
from course.models import CourseModel
from .models import (MultiChoiceQuestion, Question, QuestionGroup, AssessmentPreference,
                     QuestionGroupStatus, MultiChoiceScripts, StudentMultiChoiceAnswer
                     )
from django.forms import formset_factory, inlineformset_factory
from eAssessmentSystem.tool_utils import admin_required_message, is_lecture, get_http_forbidden_response
from django.contrib.auth import get_user
from student.models import Student
from django.utils import timezone
from django.core.paginator import Paginator


class QuestionGroupCreateView(LoginRequiredMixin, CreateView):
    model = QuestionGroup
    form_class = QuestionGroupCreateForm
    template_name = "assessment/questionGroup_createview.html"

    def is_lecture_course_master(self):
        course = get_object_or_404(CourseModel, name=self.kwargs.get("courseName"), pk=self.kwargs.get("coursePK"))
        return course.lecture.profile == self.request.user

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
        if "Course with this type of assessment already exists" in form_.non_field_errors():
            form_.add_error("title", "Course with this type of assessment already exists")
        return super(QuestionGroupCreateView, self).form_invalid(form_)


class QuestionGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = QuestionGroup
    fields = ("title", "total_marks", "questions_type", "is_share_total_marks")
    template_name = "assessment/questionGroup_createview.html"

    def is_lecture_course_master(self):
        course = get_object_or_404(CourseModel, name=self.kwargs.get("courseName"), pk=self.kwargs.get("coursePK"))
        return course.lecture.profile == self.request.user

    def get(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master() and self.get_question_group().status == QuestionGroupStatus.PREPARED:
            return super(QuestionGroupUpdateView, self).get(*args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response("We can not help you with that")
        else:
            return get_http_forbidden_response()

    def get_question_group(self):
        return get_object_or_404(QuestionGroup, pk=self.kwargs.get("pk"), title=self.kwargs.get("title"))

    def post(self, *args, **kwargs):
        user = get_user(self.request)
        if user.is_lecture and self.is_lecture_course_master() and self.get_question_group().status == QuestionGroupStatus.PREPARED:
            return super(QuestionGroupUpdateView, self).post(*args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with this.")
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(QuestionGroupUpdateView, self).get_context_data(**kwargs)
        ctx["title"] = "Update %s" % self.object
        return ctx


class CreateTheoryQuestion(LoginRequiredMixin, View):
    template_name = "assessment/prepareTheoryQuestions.html"
    question_formset = inlineformset_factory(parent_model=QuestionGroup, model=Question, form=QuestionCreateForm,
                                             can_delete=True, min_num=1, validate_min=True)

    def get_question_group_instance(self):
        question_group_pk = self.kwargs.get("QGPK")
        question_group_title = self.kwargs.get("QGT")
        return get_object_or_404(QuestionGroup, title=question_group_title, pk=question_group_pk)

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user and user.is_lecture:
            question_group_instance = self.get_question_group_instance()
            ctx = {
                "questionFormSet": self.question_formset(instance=question_group_instance),
                "question_group": question_group_instance,
                "title": "Prepare Theory Question",
            }
            return render(request, template_name=self.template_name, context=ctx)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user and user.is_lecture:
            question_group_instance = self.get_question_group_instance()
            question_form_set = self.question_formset(request.POST, instance=question_group_instance)
            if question_form_set.is_valid():
                question_form_set.save(True)
                return redirect("assessment:question_grp_detail", courseName=question_group_instance.course,
                                title=question_group_instance.title, pk=question_group_instance.pk)
            else:
                ctx = {
                    "questionFormSet": self.question_formset,
                    "question_group": question_group_instance,
                    "title": "Prepare Theory Questions",
                }
                return render(request, template_name=self.template_name, context=ctx)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")


class CreateMultipleChoiceQuestion(LoginRequiredMixin, View):
    """
    TODO check if the lecture is the course master before granting permission
    """
    objectives_formset = formset_factory(form=MultiChoiceQuestionCreateForm, min_num=2, can_delete=True,
                                         validate_min=True, extra=2,
                                         formset=BaseOptionsFormSet)
    question_form_class = QuestionCreateForm
    template_name = "assessment/prepareMCQ.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"), pk=self.kwargs.get("QGPK"))
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
            "course": self.question_group.course,
            "is_new": True,
            "question_number": self.question_group.question_set.count() + 1,
        }

    def post(self, request, *args, **kwargs):
        user = get_user(request)

        if user.is_lecture and user.is_active and self.is_lecture_course_master():
            question_form = self.question_form_class(request.POST)
            objectives = self.objectives_formset(request.POST)
            if question_form.is_valid() and objectives.is_valid:
                question_instance = question_form.save(False)
                question_instance.group = self.question_group
                question_instance.save()
                for objective in objectives:
                    obj_ins = objective.save(False)
                    obj_ins.question = question_instance
                    obj_ins.question_number = 1
                    obj_ins.save()
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

    def get(self, request, *args, **kwargs):
        if request.user.is_active and request.user.is_lecture:
            return super(AssessmentQuestionGroupDetailView, self).get(request, *args, **kwargs)
        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentQuestionGroupDetailView, self).get_context_data(**kwargs)
        ctx["questions"] = self.object.question_set.all()
        ctx["title"] = "Question Groups"
        return ctx


class EditTheoryQuestion(LoginRequiredMixin, UpdateView):
    """
    TODO check question status before proceeding to allow editing
    """
    model = Question
    template_name = "assessment/edit_question.html"
    form_class = QuestionCreateForm

    def is_lecture_course_master(self):
        self.question_ins = get_object_or_404(self.model, pk=self.kwargs.get("pk"))
        return self.question_ins.group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_active and user.is_lecture and self.is_lecture_course_master() and self.question_ins.group.status == QuestionGroupStatus.PREPARED:
            return super(EditTheoryQuestion, self).get(request=request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")
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
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that.")
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("group_title"),
                                                course=self.kwargs.get("coursePK"))
        user = get_user(request)
        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            return super(DeleteQuestion, self).post(request, *args, **kwargs)
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
                                               extra=2,
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
        }

    def get(self, request, *args, **kwargs):
        user = get_user(request)

        if is_lecture(
                user) and self.is_lecture_course_master() and self.question_instance.group.status == QuestionGroupStatus.PREPARED:
            ctx = self.get_content_data()
            ctx["multiChoiceQFormset"] = self.objectives_formset(instance=self.question_instance)
            ctx["questionForm"] = self.question_form_class(instance=self.question_instance)

            return render(request, template_name=self.template_name, context=ctx)
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


class AssessmentView(LoginRequiredMixin, View):
    template_name = "assessment/assessment_View.html"

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(user):
            return render(request, self.template_name, self.get_content_data())
        elif user:
            return get_http_forbidden_response()
        else:
            return redirect("accounts:loginPage")

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
        course = get_object_or_404(CourseModel, name=course_name_pk[0], pk=course_name_pk[1])
        question_groups = self.model.objects.filter(course=course)
        return question_groups


class DeleteQuestionGroup(LoginRequiredMixin, DeleteView):
    model = QuestionGroup
    template_name = "assessment/delete_question_view.html"

    def is_lecture_course_master(self):
        self.course = get_object_or_404(CourseModel, pk=self.kwargs.get("coursePK"), name=self.kwargs.get("courseName"))
        return self.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(user) and self.is_lecture_course_master():
            return super(DeleteQuestionGroup, self).get(request, *args, **kwargs)
        elif is_lecture(user):
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if is_lecture(user) and self.is_lecture_course_master():
            return super(DeleteQuestionGroup, self).post(request, *args, **kwargs)
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
    template_name = "assessment/conductAssessment.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, pk=self.kwargs.get("question_group_pk"),
                                                title=self.kwargs.get("question_group_title"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            return super(ConductAssessment, self).get(request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that. this time")
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(ConductAssessment, self).get_context_data(**kwargs)
        if self.question_group.status == "prepared":
            ctx["title"] = "Conduct"
            ctx["total_student"] = self.get_ready_student(self.question_group.course)
            ctx["calculated_total_marks"] = sum([q.max_mark or 0 for q in self.question_group.question_set.all()])
            ctx["student_level"] = self.question_group.course.level
            ctx["course"] = self.question_group.course
        else:
            ctx["has_conducted"] = True
        ctx["question_group"] = self.question_group
        return ctx

    def get_ready_student(self, course):
        return Student.objects.filter(programme__coursemodel=course, level=course.level).count()


class MarkAssessment(LoginRequiredMixin, TemplateView):
    template_name = "assessment/mark_assessment.html"

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture:
            return super(MarkAssessment, self).get(request, *args, **kwargs)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(MarkAssessment, self).get_context_data(**kwargs)
        ctx["title"] = "Mark"
        return ctx


class AssessmentPreferenceCreateView(LoginRequiredMixin, CreateView):
    model = AssessmentPreference
    form_class = AssessmentPreferenceCreateForm
    template_name = "assessment/assessment_preference.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master():
            return super(AssessmentPreferenceCreateView, self).get(request, *args, **kwargs)
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master():
            returns = super(AssessmentPreferenceCreateView, self).post(request, *args, **kwargs)
            self.question_group.preference = self.object
            self.question_group.save()
            return returns

        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentPreferenceCreateView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "%s %s Assessment Preference" % (
        self.question_group.course, self.question_group.get_title_display())
        return ctx

    def get_success_url(self):
        return self.question_group.get_absolute_url()


class ConductingAssessment(LoginRequiredMixin, TemplateView):
    template_name = "assessment/conducting_assessment.html"

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master() and self.question_group.status == QuestionGroupStatus.PREPARED:
            self.question_group.status = "conduct"
            if not self.question_group.preference:
                preference = AssessmentPreference.objects.create(
                    due_date=timezone.now(),
                    environment="any",
                )
                self.question_group.preference = preference
            self.question_group.save()
            return super(ConductingAssessment, self).get(request, *args, **kwargs)
        elif self.is_lecture_course_master():
            return get_http_forbidden_response(message="We can not help you with that. this time")
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(ConductingAssessment, self).get_context_data(**kwargs)
        ctx["question_group"] = self.question_group
        ctx["student_total"] = self.get_student_total()
        ctx["student_total_active"] = self.get_student_total()
        return ctx

    def get_student_total(self):
        course = self.question_group.course
        return Student.objects.filter(level=course.level, programme=course.programme).count()


class StudentAssessmentView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/student_assesssment_view.html"

    def get_student(self):
        return get_user(self.request).student

    def get(self, request, *args, **kwargs):
        student = self.get_student()

        if student and student.programme:
            return super(StudentAssessmentView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def get_question_groups(self):
        student = self.get_student()
        return QuestionGroup.objects.filter(course__level_id=student.level_id, course__programme=student.programme,
                                            status=QuestionGroupStatus.CONDUCT)

    def get_context_data(self, **kwargs):
        ctx = super(StudentAssessmentView, self).get_context_data(**kwargs)
        ctx["student"] = self.get_student()
        ctx["title"] = "Student"
        ctx["question_groups"] = self.get_question_groups()
        return ctx


class StudentResultTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/student_result.html"

    def get_student(self):
        return get_user(self.request).student

    def get(self, request, *args, **kwargs):
        student = self.get_student()
        if student and student.programme:
            return super(StudentResultTemplateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(StudentResultTemplateView, self).get_context_data(**kwargs)
        ctx["student"] = self.get_student()
        ctx["title"] = "Student"
        return ctx


class GenerateQMarksRedirectQGroupRV(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.question_group_instance.get_absolute_url()

    def is_lecture_course_master(self):
        user = get_user(self.request)
        return user.is_lecture and user == self.question_group_instance.course.lecture.profile

    def get_question_group(self):
        self.question_group_instance = get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"),
                                                         pk=self.kwargs.get("QGPK"))
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

    def is_lecture_course_master(self):
        self.question_group = get_object_or_404(QuestionGroup, title=self.kwargs.get("question_group_title"),
                                                pk=self.kwargs.get("question_group_pk"))
        return self.question_group.course.lecture.profile == self.request.user

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master():
            return super(AssessmentPreferenceUpdateView, self).get(request, *args, **kwargs)
        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture and self.is_lecture_course_master():
            returns = super(AssessmentPreferenceUpdateView, self).post(request, *args, **kwargs)
            self.question_group.preference = self.object
            self.question_group.save()
            return returns

        elif user.is_lecture:
            return get_http_forbidden_response()
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(AssessmentPreferenceUpdateView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "%s %s Assessment Preference" % (
        self.question_group.course, self.question_group.get_title_display())
        return ctx

    def get_success_url(self):
        return self.question_group.get_absolute_url()


class StudentAssessingTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "assessment/student_assessing.html"

    def get_question_group(self):
        return get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"), pk=self.kwargs.get("QGPK"))

    def student_can_enter_hall(self):
        student = self.get_student()
        question_group = self.get_question_group()
        return student and student.programme == question_group.course.programme and student.level == question_group.course.level

    def get(self, request, *args, **kwargs):
        if self.student_can_enter_hall():
            return super(StudentAssessingTemplateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

    def get_context_data(self, **kwargs):
        ctx = super(StudentAssessingTemplateView, self).get_context_data(**kwargs)
        ctx["question_group"] = self.get_question_group()
        ctx["q_preference"] = self.get_question_group().preference
        ctx["course"] = self.get_question_group().course
        ctx["student"] = self.get_student()
        current_year = timezone.now().date().year
        ctx["academic_year"] = current_year - 1, current_year
        return ctx

    def get_student(self):
        return self.request.user.student


class MultiChoiceQuestionsExaminationView(LoginRequiredMixin, View):
    template_name = "assessment/multichoice_exam.html"
    student_multi_choice_answer_form_class = StudentMultiChoiceAnswerForm

    def is_student_qualified(self):
        self.student = self.request.user.student
        course = self.question_instance.group.course
        return self.student and self.student.level == course.level and self.student.programme == course.programme

    def get_paginator(self):
        return Paginator()

    def get_script(self):
        question_group = self.question_instance.group
        instance, created = MultiChoiceScripts.objects.get_or_create(
            student_id=self.student.id,
            course_id=question_group.course_id,
            question_group_id=question_group.id
        )
        print("MultiChoiceScripts SCRIPTS IS_CREATED = ", created)
        return instance

    def get_instance(self):
        instance, created = StudentMultiChoiceAnswer.objects.get_or_create(
            question_id=self.question_instance.id,
            script=self.get_script()
        )
        print("StudentMultiChoiceAnswer IS_CREATED = ", created)
        return instance

    def get(self, request, *args, **kwargs):
        question_instance = self.get_question_instance()
        if isinstance(question_instance, Question):
            if self.is_student_qualified():
                ctx = self.get_context_data()
                ctx["answer_form"] = self.student_multi_choice_answer_form_class()
                return render(request, template_name=self.template_name, context=ctx)
            else:
                return get_http_forbidden_response()
        else:
            return question_instance

    def post(self, request, *args, **kwargs):
        question_instance = self.get_question_instance()
        if isinstance(question_instance, Question):
            if self.is_student_qualified():
                student_multi_choice_answer_form_class = self.student_multi_choice_answer_form_class(question_instance=question_instance, instance=self.get_instance(), data=request.POST)
                if student_multi_choice_answer_form_class.is_valid():
                    student_multi_choice_answer_form_class.save(True)
                    return redirect("assessment:MCQ_exam_start", course_code=self.question_instance.group.course.code, QGT=self.question_instance.group.title, question_pk=None)
            else:
                return get_http_forbidden_response()
        else:
            return question_instance

    def get_context_data(self):
        return {
            "title": "%s start" % self.question_instance.group.get_title_display(),
            "question": self.question_instance,
            "today": timezone.now()
        }

    def get_successful_url(self):
        # TODO return redirect to results
        pass

    def get_initial(self):
        return {
            "student": self.student
        }

    def get_question_group(self):
        self.question_group_instance = get_object_or_404(QuestionGroup, title=self.kwargs.get("QGT"), pk=self.kwargs.get("QGPK"), course__code=self.kwargs.get("course_code"))
        return self.question_group_instance


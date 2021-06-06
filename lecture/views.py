from django.shortcuts import render, get_object_or_404, redirect
from .models import LectureModel
from .forms import LectureCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView, ListView, TemplateView
from accounts.forms import UserCreateForm
from eAssessmentSystem.tool_utils import admin_required_message, get_http_forbidden_response, get_status_tips
from assessment.models import QuestionGroup, QuestionGroupStatus, CourseModel


class LectureCreateView(LoginRequiredMixin, View):
    model = LectureModel
    lecture_form_class = LectureCreateForm
    profile_form = UserCreateForm
    template_name = "lecture/add.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            ctx = {
                "lecture_form":self.lecture_form_class(),
                "profile_form":self.profile_form(),
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
                "pageTitle": "Add Lecture"
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
        try:
            lecture = self.request.user.lecturemodel
            self.question_group_queryset = QuestionGroup.objects.filter(
                course__lecture=lecture,
                status__in=(QuestionGroupStatus.CONDUCTED, QuestionGroupStatus.PUBLISHED, QuestionGroupStatus.MARKED)
            )
        except AttributeError:
            raise get_http_forbidden_response()

    def get(self, request, *args, **kwargs):
        self.init_lecture_course_question_groups()
        return super(LectureStudentScripts, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(LectureStudentScripts, self).get_context_data(**kwargs)

        # Add Question_groups to context data and return
        ctx["question_group"] = self.question_group_queryset
        return ctx

    def get_template_names(self):
        template_name_1 = "lecture/scripts/all_scripts_lecture.html"
        template_name = "lecture/scripts/view.html"
        action = self.request.GET.get("action")
        if action == "listAllQS":
            return template_name_1
        else:
            return template_name


class LectureStudentScriptMarkView(LoginRequiredMixin, TemplateView):
    pass


class QuizTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "lecture/scripts/quiz_view.html"

    def get_courses(self):
        lecture_model = self.request.user.lecturemodel
        return CourseModel.objects.filter(
            lecture=lecture_model,
            semester=lecture_model.profile.generalsetting.semester
        )

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


class MarkingSchemeCreateView(LoginRequiredMixin, View):
    pass


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

    def get_context_object_name(self, obj=None):
        print("QuestionGroupDetailView OBJ::\t", obj)
        return "question_group_instance"

    def get_object(self, queryset=None):
        return self.question_group_instance

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture:
            self.init_question_group_instance()
            if self.question_group_instance.status not in (QuestionGroupStatus.PREPARED, QuestionGroupStatus.CONDUCT):
                return super(QuestionGroupDetailView, self).get(request, *args, **kwargs)
            else:
                return render(request, "assessment/status_not_allowed.html", {
                    "question_group_instance": self.question_group_instance,
                    "lecture_details": True,
                    "tip": get_status_tips(self.question_group_instance, QuestionGroupStatus)
                })
        else:
            return get_http_forbidden_response()


from course.models import CourseModel
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import StudentRegisterForm, PasswordSetForm
from accounts.forms import StudentProfileCreateForm
from .models import Student
from programme.models import Programme
from eAssessmentSystem.tool_utils import admin_required_message, get_not_allowed_render_response, request_level_check
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist


class StudentCreateView(View):
    """
    Create student with profile(user obj), department, programme offering,
    :return render to success page (student home page)
    """
    student_form_class = StudentRegisterForm
    profile_form_class = StudentProfileCreateForm
    pwd_set_form_class = PasswordSetForm
    template_name = 'student/register_form.html'

    def get(self, *args, **kwargs):
        lecture = None
        if self.request.user.is_authenticated and self.request.user.is_lecture:
            lecture = self.request.user.lecturemodel
        ctx = {
            "HeaderTitle": "Student Registration",
            "student_form": self.student_form_class(initial=self.get_initial(), lecture=lecture, prefix="student_form"),
            "profile_form": self.profile_form_class(prefix="profile_form"),
            "pwd_form": self.pwd_set_form_class(prefix="password_form"),
            "programme_default": self.request.session.get("programme_pk")
        }
        return render(self.request, self.template_name, context=ctx)

    def post(self, *args, **kwargs):
        lecture = None
        if self.request.user.is_authenticated and self.request.user.is_lecture:
            lecture = self.request.user.lecturemodel
        profile_form = self.profile_form_class(self.request.POST, prefix="profile_form")
        student_form = self.student_form_class(data=self.request.POST, prefix="student_form", lecture=lecture)

        pwd_form = self.pwd_set_form_class(self.request.POST, prefix="password_form")
        if student_form.is_valid() and profile_form.is_valid() and pwd_form.is_valid():
            profile = profile_form.save(False)
            profile.username = student_form.cleaned_data["index_number"]
            profile.set_password(pwd_form.cleaned_data["password"])
            profile.save()
            student = student_form.save(False)
            student.profile = profile
            student.save()
            programme = self.get_initial().get("programme")
            if programme:
                return redirect(programme.get_absolute_url())
            elif self.request.user.is_authenticated and self.request.user.is_lecture:
                self.request.session["registered_student_pk"] = student.pk
                return redirect("student:registered")

            login(self.request, user=profile)
            return redirect("landing-page")
        ctx = {
            "HeaderTitle": "Student Registration",
            "student_form": student_form,
            "profile_form": profile_form,
            "pwd_form": pwd_form,
            "number_has_error": profile_form.has_error("phone_number")
        }
        return render(self.request, self.template_name, context=ctx)

    def get_initial(self):
        initial = {}
        programme_pk = self.request.session.get("programme_pk")
        if programme_pk:
            try:
                initial["programme"] = Programme.objects.get(pk=programme_pk)
            except Programme.DoesNotExist:
                initial = {}
        return initial


class SuccessfulStudentRegistration(LoginRequiredMixin, TemplateView):
    template_name = "student/registered.html"

    def get_context_data(self, **kwargs):
        ctx = super(SuccessfulStudentRegistration, self).get_context_data(**kwargs)
        ctx["student"] = get_object_or_404(Student, pk=self.request.session.get("registered_student_pk"))

        # try:
        #     del self.request.session["registered_student_pk"]
        # except KeyError:
        #     pass
        return ctx

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_lecture):
            return super(SuccessfulStudentRegistration, self).get(request, *args, **kwargs)
        else:
            return render(request, template_name="snippet/notAva.html", context={})


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "student/listview.html"

    def get_ordering(self):
        return "programme", "level"

    def get_queryset(self):
        query = self.request.GET.get("query")
        if query:
            return self.model.objects.search(query)
        else:
            return self.model.objects.all()

    def get_context_data(self, object_list=None, **kwargs):
        ctx = super(StudentListView, self).get_context_data(object_list=object_list, **kwargs)
        ctx["query"] = self.request.GET.get("query")
        return ctx

    def get(self, *args, **kwargs):
        return request_level_check(StudentListView, self, False, False, *args, **kwargs)


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "student/detail.html"

    def get_student(self):
        try:
            return self.request.user.student
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        user = request.user
        is_student = self.get_student() == self.get_object()
        if user.is_active and (is_student or user.is_lecture  or user.is_admin  or user.is_superuser):
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.object.profile
        try:
            ctx["courses"] = CourseModel.objects.filter(programme=self.object.programme, level=self.object.level, semester=self.object.profile.generalsetting.semester)
        except ObjectDoesNotExist:
            ctx["generalsetting_error"] = True
        return ctx


class LectureStudentsListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "student/lecture_all_student.html"

    def get_queryset(self):
        query = self.request.GET.get("query")
        return self.model.objects.search_lecture_student(query=query, lecture=self.request.user.lecturemodel)

    def get(self, request, *args, **kwargs):
        if request.user.is_lecture and request.user.is_authenticated and request.user.is_active:
            return super(LectureStudentsListView, self).get(request, *args, **kwargs)
        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(LectureStudentsListView, self).get_context_data(object_list=object_list, **kwargs)
        queryset = self.get_queryset()
        query = self.request.GET.get("query")
        ctx["query"] = query
        ctx["has_student"] = queryset if queryset else query
        return ctx

    def get_ordering(self):
        return "programme", "level"

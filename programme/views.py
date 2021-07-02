from .forms import ProgrammeCreateForm, Programme
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from eAssessmentSystem.tool_utils import admin_required_message, request_level_check, general_setting_not_init
from department.models import Department
from course.form import CourseModel
from django.db.models import ObjectDoesNotExist


class ProgrammeCreateView(LoginRequiredMixin, CreateView):
    model = Programme
    form_class = ProgrammeCreateForm
    template_name = "programme/createview.html"
    
    def get(self, *args, **kwargs):
        user = self.request.user
        get_object_or_404(Department, name=self.kwargs.get("departmentName"), pk=self.kwargs.get("departmentPK"))
        if user.is_active and user.is_admin:
            return super(ProgrammeCreateView, self).get(*args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:admin-login-page")

    def get_initial(self):
        initials = super(ProgrammeCreateView, self).get_initial()
        initials["department"] = get_object_or_404(Department, name=self.kwargs.get("departmentName"), pk=self.kwargs.get("departmentPK"))
        return initials

    def post(self, *args, **kwargs):
        user = self.request.user
        if user.is_active and user.is_admin:
            return super(ProgrammeCreateView, self).post(*args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:admin-login-page")

    def get_success_url(self):
        return self.object.department.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super(ProgrammeCreateView, self).get_context_data(**kwargs)
        ctx["department"] = self.kwargs["departmentName"]
        ctx["department_pk"] = self.kwargs["departmentPK"]
        return ctx


class ProgrammeDetailView(LoginRequiredMixin, DetailView):
    model = Programme
    template_name = "programme/detailview.html"

    def get_context_data(self, **kwargs):
        ctx = super(ProgrammeDetailView, self).get_context_data(**kwargs)
        if self.object.department:
            ctx["department"] = self.object.department
            if self.request.user.is_staff:
                ctx["courses"] = self.object.coursemodel_set.all()
            elif self.request.user.is_lecture:
                # ctx["courses"] = self.request.user.lecturemodel.coursemodel_set.all().filter(programme=programme)
                ctx["courses"] = CourseModel.objects.get_lecture_courses(self.request.user.lecturemodel, programme=self.object)

            course_name = self.request.session.get("course_deleted_name")
            course_deleted = self.request.session.get("has_course_deleted")
            if course_deleted and course_name:
                ctx["course_deleted_name"] = course_name
                del self.request.session["has_course_deleted"]
                del self.request.session["course_deleted_name"]

        if self.request.user.is_staff:
            self.request.session["programme_name"] = self.object.name
            self.request.session["programme_pk"] = self.object.pk
        return ctx

    def get(self, *args, **kwargs):
        if self.request.user.is_active and (self.request.user.is_staff or self.request.user.is_lecture):
            try:
                return super(ProgrammeDetailView, self).get(*args, **kwargs)
            except ObjectDoesNotExist as err:
                return general_setting_not_init(self.request)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:staff-login-page")


class ProgrammeUpdateView(UpdateView):
    model = Programme
    template_name = "programme/createview.html"
    fields = ("name", )

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get(self, *args, **kwargs):
        self.request.session["admin_required"] = admin_required_message(self.request.user)
        return request_level_check(ProgrammeUpdateView, self, False, False, *args, **kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if user.is_active and user.is_staff:
            return super(ProgrammeUpdateView, self).post(*args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:admin-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(ProgrammeUpdateView, self).get_context_data(**kwargs)
        ctx["headerTitle"] = "Update"
        ctx["is_update"] = True
        return ctx

    def get_initial(self):
        initials = super(ProgrammeUpdateView, self).get_initial()
        return initials

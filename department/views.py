from django.shortcuts import redirect, get_object_or_404, render
from .forms import DepartmentCreateForm, Department, DepartmentSetChangeHODForm
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import is_safe_url
from programme.forms import ProgrammeCreateForm
from course.models import CourseModel
from student.models import Student
from eAssessmentSystem.tool_utils import (
    admin_required_message, get_http_forbidden_response, get_not_allowed_render_response,
    get_back_url
)


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    template_name = "department/createview.html"
    model = Department
    form_class = DepartmentCreateForm
    
    def get(self, *args, **kwargs):
        if self.request.user.is_admin and self.request.user.is_authenticated:
            return super(DepartmentCreateView, self).get(*args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def post(self, request, *args, **kwargs):
        if request.user.is_admin:
            return super(DepartmentCreateView, self).post(request, *args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def form_valid(self, form):
        form_ = form
        return super(DepartmentCreateView, self).form_valid(form_)

    def get_context_data(self, **kwargs):
        ctx = super(DepartmentCreateView, self).get_context_data(**kwargs)
        ctx["title"] = "Add new Department"
        ctx["back_url"] = get_back_url(self.request)
        return ctx


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = "department/detailview.html"
    programme_form = ProgrammeCreateForm

    def get_context_data(self, **kwargs):
        ctx = super(DepartmentDetailView, self).get_context_data(**kwargs)
        if self.object.programme_set.exists():
            ctx["programmes"] = self.object.programme_set.all()
        ctx["modal_form"] = self.programme_form(self.request.POST)
        return ctx

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_active and (user.is_admin or user.is_lecture):
            return super(DepartmentDetailView, self).get(*args, **kwargs)
        else:
            return get_not_allowed_render_response(self.request)


class DepartmentGridView(LoginRequiredMixin, ListView):
    model = Department
    template_name = "department/listview.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_admin and self.request.user.is_active:
            return super(DepartmentGridView, self).get(*args, **kwargs)
        else:
            self.request.session[
                "admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(DepartmentGridView, self).get_context_data(object_list=object_list, **kwargs)
        ctx["queryPlaceholder"] = "Search for any department"
        query = self.request.GET.get("query")
        if query:
            ctx["query"] = query
            len_list = self.object_list.count()
            if len_list:
                query_info = "%d Departments matches" % len_list
            else:
                query_info = "No Department <u>name</u> or <u>short name</u> matches"
        else:
            len_list = self.object_list.count()
            if len_list == 1:
                query_info = "We have %s department registered in this e-Assessment System." % len_list
            elif len_list > 1:
                query_info = "We have %s departments registered in this e-Assessment System." % len_list
            else:
                query_info = "no department registered in the assessment system."
        ctx["queryInfo"] = query_info
        return ctx

    def get_queryset(self):
        q = self.request.GET.get("query")
        self.model.objects.filter()
        if q:
            return self.model.objects.search(q)
        else:
            return super(DepartmentGridView, self).get_queryset()


class StudentDepartmentTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "department/student.html"

    def get_student(self):
        return self.request.user.student

    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            if student and student.programme:
                return super(StudentDepartmentTemplateView, self).get(request, *args, **kwargs)
            else:
                return get_http_forbidden_response()
        except Exception as err:
            print("Department.views 107 err", err)
            return get_not_allowed_render_response(request)

    def get_course(self):
        student = self.get_student()
        course = CourseModel.objects.filter(programme=student.programme, level=student.level)
        return course

    def get_class_mate(self):
        student =self.get_student()
        return Student.objects.filter(programme=student.programme, level=student.level)

    def get_context_data(self, **kwargs):
        ctx = super(StudentDepartmentTemplateView, self).get_context_data(**kwargs)
        student = self.get_student()
        ctx["programme"] = student.programme
        ctx["courses"] = self.get_course()
        ctx["student"] = student
        ctx["class_mates"] = self.get_class_mate()
        return ctx


class HodStatusUpdateView(LoginRequiredMixin, View):
    template_name = "department/hod/change_hod.html"
    model = Department
    form_class = DepartmentSetChangeHODForm

    def get_context_data(self, **kwargs):
        return {
            "title": "HOD Status",
        }

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model,
            pk=self.kwargs["pk"],
            name=self.kwargs["name"],
        )

    def get_success_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url
        else:
            return self.get_object().get_absolute_url()

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data()
        department_instance = self.get_object()
        ctx["form"] = self.form_class(instance=department_instance, initial=self.get_initial(department_instance))
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        ctx = self.get_context_data()
        department_instance = self.get_object()
        form_instance = self.form_class(instance=department_instance, data=self.request.POST,
                                        initial=self.get_initial(department_instance))
        if form_instance.is_valid():
            hod = form_instance.cleaned_data["hod"]
            department_instance.hod = hod.profile
            department_instance.save()
            return redirect(self.get_success_url())

        ctx["form"] = form_instance

        return render(request, self.template_name, ctx)

    def get_initial(self, department):
        try:
            return {
                "hod": department.hod
            }
        except AttributeError:
            pass
        return {}


class HodDashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "department/hod/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super(HodDashboardTemplateView, self).get_context_data(**kwargs)
        ctx["title"] = "HOD Dashboard"
        return ctx

    def get(self, request, *args, **kwargs):
        from django.db.models import ObjectDoesNotExist
        try:
            if self.request.user.is_hod:
                return super(HodDashboardTemplateView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            pass
        return get_not_allowed_render_response(request)

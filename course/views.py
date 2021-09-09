from django.db.models.query_utils import Q
from django.shortcuts import redirect, get_object_or_404, reverse
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import CourseModel, CourseCreateForm
from eAssessmentSystem.tool_utils import admin_required_message
from programme.models import Programme
from django.utils.http import is_safe_url


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = CourseModel
    form_class = CourseCreateForm
    template_name = "course/add.html"
    programme_model = Programme

    def post(self, request, *args, **kwargs):
        if self.request.user.is_admin and self.request.user.is_active:
            return super(CourseCreateView, self).post(request=request, *args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_admin and self.request.user.is_active:
            return super(CourseCreateView, self).get(request=request, *args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(CourseCreateView, self).get_context_data(**kwargs)
        p_name, p_pk = self.request.session.get("programme_name"), self.request.session.get("programme_pk")
        if p_name and p_pk:
            programme = get_object_or_404(Programme, pk=p_pk, name=p_name)
            ctx["programme"] = programme
        return ctx

    def get_initial(self):
        p_name, p_pk = self.request.session.get("programme_name"), self.request.session.get("programme_pk")
        programme = get_object_or_404(Programme, pk=p_pk, name=p_name)

        initials = super(CourseCreateView, self).get_initial()
        initials["programme"] = programme
        return initials

    def get_success_url(self):
        p_name, p_pk = self.request.session.get("programme_name"), self.request.session.get("programme_pk")
        programme = get_object_or_404(Programme, pk=p_pk, name=p_name)
        instance = self.object
        instance.programme = programme
        instance.save()
        del self.request.session["programme_name"]
        del self.request.session["programme_pk"]

        return programme.get_absolute_url()


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = CourseModel
    template_name = "course/detailview.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_active and (self.request.user.is_lecture or self.request.user.is_staff):
            return super(CourseDetailView, self).get(request=request, *args, **kwargs)
        else:
            self.request.session["staff_required"] = admin_required_message(self.request.user)
            return redirect("accounts:staff-login-page")

    def get_context_data(self, **kwargs):
        ctx = super(CourseDetailView, self).get_context_data(**kwargs)
        ctx["title"] = self.object.name.title() + " Assessment"
        ctx["back_url"] = self.get_back_url()
        return ctx

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url
        return


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseModel
    template_name = "course/deleteview.html"
    parent_cls = None

    def get_success_url(self):
        if self.parent_cls:
            parent = self.parent_cls
        else:
            p_name = self.request.POST.get("course_parent_name")
            p_pk = self.request.POST.get("course_parent_pk")
            parent = get_object_or_404(Programme, pk=p_pk, name=p_name)
        return reverse("department:programme:detail", kwargs=dict(programName=parent.name, pk=parent.pk))

    def post(self, request, *args, **kwargs):
        if self.request.user.is_active and self.request.user.is_staff:
            return super(CourseDeleteView, self).post(request, *args, **kwargs)
        else:
            self.request.session["admin_required"] = admin_required_message(self.request.user)
            return redirect("accounts:admin-login-page")

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_active and user.is_admin:
            return super(CourseDeleteView, self).get(*args, **kwargs)
        else:
            self.request.session["admin_require"] = admin_required_message(user)
            return redirect("accounts:admin-login-page")

    def delete(self, request, *args, **kwargs):
        self.request.session["has_course_deleted"] = True
        self.request.session["course_deleted_name"] = self.request.POST.get("course_name")
        self.parent_cls = get_object_or_404(Programme, pk=self.kwargs["course_programme_pk"])
        return super(CourseDeleteView, self).delete(request, *args, **kwargs)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseModel
    template_name = "course/updateview.html"
    fields = "__all__"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_active and (self.request.user.is_lecture or self.request.user.is_staff):
            return super(CourseUpdateView, self).get(request=request, *args, **kwargs)
        else:
            self.request.session["staff_required"] = admin_required_message(self.request.user)
            return redirect("accounts:staff-login-page")

    def post(self, request, *args, **kwargs):
        if self.request.user.is_active and (self.request.user.is_admin or self.request.user.is_staff):
            return super(CourseUpdateView, self).post(request=request, *args, **kwargs)
        else:
            self.request.session["staff_required"] = admin_required_message(self.request.user)
            return redirect("accounts:staff-login-page")


class LectureCourseListView(LoginRequiredMixin, ListView):
    template_name = "course/lecture/courses.html"
    model = CourseModel

    def get_queryset(self):
        queryset = self.model.objects.get_lecture_courses(self.request.user.lecturemodel)
        searchCourse = self.request.GET.get("searchCourse")
        if searchCourse:
            searchCourse = searchCourse.strip().lstrip()
            return queryset.filter(Q(name__icontains=searchCourse)|Q(code__icontains=searchCourse))
        return queryset
    
    def get_context_object_name(self, object_list=None)->str:
        return "courses_list"
    
    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)
        searchCourse = self.request.GET.get("searchCourse")
        ctx["title"] = "Your Courses"
        if searchCourse:
            ctx["title"] = '"%s"' % searchCourse
        ctx["searchCourse"] = searchCourse
        return ctx
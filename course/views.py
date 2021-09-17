from django.db.models.query_utils import Q
from django.shortcuts import redirect, get_object_or_404, reverse, render
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import CourseModel, CourseCreateForm
from eAssessmentSystem.tool_utils import admin_required_message, get_not_allowed_render_response, get_back_url
from programme.models import Programme
from lecture.models import LectureModel
from django.db.models import ObjectDoesNotExist


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
        course = self.get_object()
        user = request.user
        if (course.lecture.profile == user) or user.is_admin:
            return super(CourseDetailView, self).get(request=request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
                pk=self.kwargs["pk"],
                name=self.kwargs["courseName"],
        )

    def get_context_data(self, **kwargs):
        ctx = super(CourseDetailView, self).get_context_data(**kwargs)
        ctx["title"] = self.object.name.title() + " Assessment"
        ctx["back_url"] = get_back_url(self.request)
        return ctx


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
        lecturer_pk = self.kwargs.get("lecturer_pk")
        if lecturer_pk and self.request.user.is_hod:
            self.lecturer = get_object_or_404(LectureModel, pk=lecturer_pk)
            queryset = self.model.objects.get_lecture_courses(self.lecturer)
        else:
            queryset = self.model.objects.get_lecture_courses(self.request.user.lecturemodel)

        searchCourse = self.request.GET.get("searchCourse")
        if searchCourse:
            searchCourse = searchCourse.strip().lstrip()
            return queryset.filter(Q(name__icontains=searchCourse)|Q(code__icontains=searchCourse))
        return queryset
    
    def get_context_object_name(self, object_list=None) -> str:
        return "courses_list"
    
    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)
        searchCourse = self.request.GET.get("searchCourse")
        ctx["title"] = "Your Courses"
        if searchCourse:
            ctx["title"] = '"%s"' % searchCourse
        try:
            ctx["lecturer"] = self.lecturer
            ctx["semester"] = self.lecturer.profile.generalsetting.get_semester_display()
        except AttributeError:
            ctx["semester"] = self.request.user.generalsetting.get_semester_display()
        ctx["searchCourse"] = searchCourse

        return ctx

    def get(self, request, *args, **kwargs):
        try:
            return super(LectureCourseListView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)


class CourseAssignmentView(LoginRequiredMixin, TemplateView):
    template_name = "course/assignment.html"
    GET_VAR = "coursetoaddcode"
    ALERT = None
    Alert_level = None

    def init_instances(self):
        self.lecturer = get_object_or_404(LectureModel, pk=self.kwargs["lecturer_pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CourseAssignmentView, self).get_context_data(object_list=object_list, **kwargs)
        ctx["title"] = "Course Assigment"
        ctx["lecturer_name"] = self.lecturer.profile.get_full_name()
        ctx["lecturer_courses"] = self.get_lecturer_courses()
        ctx["available_courses"] = self.get_available_courses()
        ctx["get_variable"] = self.GET_VAR
        ctx["alert"] = self.ALERT
        ctx["alert_level"] = self.Alert_level
        ctx["back_url"] = get_back_url(self.request)
        return ctx

    def get(self, request, *args, **kwargs):
        try:
            if self.request.user.is_hod or self.request.user.is_admin:
                self.init_instances()
                self.add_course_to_lecturer()
                return super(CourseAssignmentView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            pass

        return get_not_allowed_render_response(request)

    def add_course_to_lecturer(self):
        course_code = self.request.GET.get(self.GET_VAR)
        if course_code:
            try:
                course = CourseModel.objects.get(code=course_code)
                if not course.lecture:
                    course.lecture = self.lecturer
                    course.save()
                    self.ALERT = "%s has been assigned to lecturer %s successfully" % (course.name,
                                                                               self.lecturer.profile.get_full_name())
                    self.Alert_level = 1
                else:
                    self.ALERT = "Sorry something just happen it seems like this course (%s) " \
                                 "already has an active lecturer (%s)" % (course.name, course.lecture)
                    self.Alert_level = 0
            except ObjectDoesNotExist:
                self.ALERT = "Sorry something just happen, please try again!"
                self.Alert_level = -1
                pass
        pass

    def get_available_courses(self):
        return CourseModel.objects.filter(lecture__isnull=True, programme__department=self.lecturer.department)

    def get_lecturer_courses(self):
        return self.lecturer.coursemodel_set.all()


class CourseUnassignmentView(LoginRequiredMixin, DetailView):
    template_name = "course/unassignment.html"

    def init_instance(self):
        self.course_instance = get_object_or_404(CourseModel, code=self.kwargs["course_code"])
        self.lecturer = self.course_instance.lecture

    def get_object(self, queryset=None):
        return self.course_instance

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_hod or user.is_admin:
            self.init_instance()
            if self.lecturer.profile != user:
                return super(CourseUnassignmentView, self).get(request, *args, **kwargs)
        return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(CourseUnassignmentView, self).get_context_data(**kwargs)
        ctx["title"] = "Un-assignment of Courses"
        ctx["lecturer_name"] = self.lecturer.profile.get_full_name()
        ctx["back_url"] = get_back_url(self.request)
        return ctx

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_hod or user.is_admin:
            self.init_instance()
            if self.lecturer.profile != user:
                if self.request.POST.get("confirmation") == "1":
                    self.course_instance.lecture = None
                    self.course_instance.save()
                    back_url = get_back_url(request)
                    if back_url:
                        return redirect(back_url)
                    else:
                        return redirect("department:programme:course:assigment", kwargs={"lecturer_pk": self.lecturer.pk})
                return self.get(request, *args, **kwargs)
        return get_not_allowed_render_response(request)


class SelectCourseToChatInView(LoginRequiredMixin, TemplateView):
    template_name = "course/chat/select_course.html"

    def get_context_data(self, **kwargs):
        ctx = super(SelectCourseToChatInView, self).get_context_data(**kwargs)
        ctx["title"] = "Select Course"
        ctx["courses"] = self.get_courses()
        return ctx

    def get_courses(self):
        user_semester = self.request.user.generalsetting.semester
        try:
            student = self.request.user.student
            return CourseModel.objects.filter(programme__student=student, level=student.level, semester=user_semester)
        except ObjectDoesNotExist:
            lecturer = self.request.user.lecturemodel
            return CourseModel.objects.filter(lecture=lecturer, semester=user_semester).order_by("programme", "level")

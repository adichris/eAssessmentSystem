from lecture.models import LectureModel
from student.models import Student, Programme
from department.models import Department
from course.models import CourseModel, CourseLevel
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, View
from .forms import UserCreateForm, StudentLoginForm, User, UserUpdateForm, ConfirmResetPasswordForm, PasswordSetForm, PasswordUpdateForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import resolve_url, redirect, reverse, render, get_object_or_404
from django.utils.http import is_safe_url
from eAssessmentSystem.tool_utils import get_not_allowed_render_response


class AddAdminView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/add_admin_view.html"


class AdminCreateView(LoginRequiredMixin ,CreateView):
    model = User
    template_name = "accounts/create/superuser_createview.html"
    form_class = UserCreateForm

    def form_valid(self, form):
        valid_ = super(AdminCreateView, self).form_valid(form)
        login(self.request, self.object)
        self.object.is_admin = True
        self.object.save()
        return valid_

    def get_context_data(self, **kwargs):
        ctx = super(AdminCreateView, self).get_context_data(**kwargs)
        ctx["title"] = "Administrator Registeration"
        return ctx
    
    def get(self, request, *args: str, **kwargs):
        if request.user.is_admin:
            msg = "Please you must also have an superuser priviliges to add administrators like you."
        else:
            msg = None
        if self.request.user.is_active and self.request.user.is_admin:
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request, message=msg)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "accounts/create/superuser_createview.html"
    form_class = UserUpdateForm
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        is_me = self.request.user == self.object
        ctx["title"] = "Edit %s Profile" % "Your" if is_me else self.object.get_full_name
        return ctx 

    def get(self, request, *args: str, **kwargs):
        if self.request.user.is_staff:
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)
    
    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if is_safe_url(next_url, self.request.get_host()):
            return next_url
        return super().get_success_url()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User

    def get_template_names(self):
        # if self.request.user.is_staff and self.request.user.is_authenticated:
        if self.request.user.is_active:
            return "accounts/detail/staff-detail.html"
        else:
            return "snippet/hasNoPerm.html"
    
    def get(self, *args, **kwargs):
        return super(UserDetailView, self).get(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super(UserDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_admin:
            ctx["departments"] = Department.objects.count()
            ctx["students"] = Student.objects.count()
            ctx["lectures"] = LectureModel.objects.count()
            ctx["programmes"] = Programme.objects.count()
            ctx["lectures"] = LectureModel.objects.count()
            ctx["admins"] = User.objects.filter(is_admin=True).count()
            ctx["courses"] = CourseModel.objects.count()
            ctx["Stulevels"] = CourseLevel.objects.all()
            ctx["students"] = Student.objects.count()
        # if user_object in kwargs == request.user return completed detail template
        return ctx


def student_login(request):
    try:
        if request.user.is_authenticated and request.user.student:
            return redirect("landing-page")
    except Exception:
        pass
    stu_login = StudentLoginForm(request.POST or None)
    if stu_login.is_valid():
        index_number = stu_login.cleaned_data.get("index_number")
        password = stu_login.cleaned_data.get("password")
        student_profile = authenticate(request, username=index_number, password=password)
        try:
            if student_profile and student_profile.student:
                login(request=request, user=student_profile)
                return redirect("landing-page")
            elif student_profile:
                stu_login.add_error(field=None, error="Having challenges logging in. try to recover your account")
            else:
                stu_login.add_error("index_number", "Enter correct login credential")
                stu_login.add_error("password", "Enter correct login credential")
        except Exception:
            stu_login.add_error("index_number", "Enter a valid credential")
            stu_login.add_error("password", "Enter a valid credential")
    ctx = {
        "form": stu_login,
        "cardHeader": " Student Login"
    }
    next_url = request.GET.get("next")
    if next_url and is_safe_url(next_url, request.get_host()):
        return redirect(next_url, permanent=True)
    return render(request, template_name="accounts/login/login.html", context=ctx)


class StaffLoginView(LoginView):
    template_name = 'accounts/login/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_lecture:
            return redirect("landing-page")
        else:
            return super(StaffLoginView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(StaffLoginView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "Staff Login"
        ctx["title"] = "Staff Login"
        ctx["admin_required"] = self.request.session.get("admin_required")
        return ctx

    def get_success_url(self):
        if self.request.user.is_lecture:
            next_url = self.request.GET.get("next")
            if next_url and is_safe_url(next_url, self.request.get_host()):
                return redirect(next_url)
            return resolve_url("accounts:user-profile", slug=self.request.user.slug, pk=self.request.user.id)
        else:
            logout(self.request)
            self.request.session["admin_required"] = "Enter a valid staff credential to login"
            return reverse("accounts:staff-login-page")


class AdminLoginView(LoginView):
    template_name = 'accounts/login/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return redirect(request.user.get_absolute_url())
        else:
            return super(AdminLoginView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(AdminLoginView, self).get_context_data(**kwargs)
        ctx["cardHeader"] = "Administrator Login"
        ctx["title"] = "Administrator Login"
        admin_required = self.request.session.get("admin_required")
        if admin_required:
            ctx["admin_required"] = admin_required
            del self.request.session["admin_required"]
            try:
                del self.request.session["admin_required"]
            except KeyError as err:
                pass
        return ctx

    def get_success_url(self):
        return resolve_url("accounts:user-profile", slug=self.request.user.slug, pk=self.request.user.id)


def user_logout(request):
    logout(request)
    request.session.clear()
    return redirect("landing-page")


class ConfirmPasswordResetView(View):
    template_name = "accounts/password/confirm_reset.html"
    form_class = ConfirmResetPasswordForm

    def get(self, request, *args, **kwargs):
        ctx = self.get_content_data()
        ctx["form"] = self.form_class()
        return render(request, template_name=self.template_name, context=ctx)
    
    def get_content_data(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return {
            "title": "Reset Your Password",
            "topic": "Reset Password",
            "notes": "When you  reset your account, you reset your data",
            "btn_name": "Confirm Password Reset"
        }
    
    def post(self, request, *args, **kwargs):
        ctx = self.get_content_data()
        form_class = self.form_class(request.POST)
        if form_class.is_valid():
            try:
                temp_user = User.objects.get(
                    username__iexact=form_class.cleaned_data["username"],
                    first_name__iexact=form_class.cleaned_data["first_name"],
                    last_name__iexact=form_class.cleaned_data["last_name"],
                    phone_number=form_class.cleaned_data["phone_number"],
                    dob=form_class.cleaned_data["dob"],
                )
            except User.DoesNotExist:
                err = "Please enter a valid credential"
                for field in form_class.fields.keys():
                    form_class.add_error(field, err)
                    ctx["has_error"] = True
            else:
                if temp_user:
                    login(request, user=temp_user)
                    return redirect("accounts:change_pwd_reset")
        ctx["form"] = form_class
        return render(request, template_name=self.template_name, context=ctx)


class ChangePasswordView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/password/confirm_reset.html"
    form_class = PasswordSetForm
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super(ChangePasswordView, self).get_context_data(**kwargs)
        ctx["btn_name"] = "Save"
        ctx["title"] = "Set Password"
        ctx["topic"] = "Create New Password"
        ctx["is_set_pwd_view"] = True
        return ctx

    def get_success_url(self):
        login(self.request, self.get_object())
        return reverse("landing-page")


class ChangePasswordUpdateView(LoginRequiredMixin, View):
    model = User
    template_name = "accounts/change_password.html"
    form_class = PasswordUpdateForm

    def get(self, request, *args, **kwargs):
        ctx = self.get_content()
        ctx["form"] = self.form_class(user=self.request.user)
        return render(request, self.template_name, ctx)

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url

    def get_content(self):
        return {
            "title": "Change password",
            "back_url": self.get_back_url()
        }

    def post(self, request, *args, **kwargs):
        ctx = self.get_content()
        form_class = self.form_class(data=request.POST, user=self.request.user)
        if form_class.is_valid():
            old_pwd = form_class.cleaned_data["old_password"]
            new_pwd = form_class.cleaned_data["new_password"]
            new_confirm_pwd = form_class.cleaned_data["confirm_new_password"]
            user = self.request.user
            if new_pwd == new_confirm_pwd:
                user.set_password(new_pwd)
                user.save()
                back_url = self.get_back_url()
                if back_url:
                    return redirect(back_url)
                else:
                    return redirect(user.get_absolute_url())
            else:
                form_class.add_error("old_password", "enter a correct password")

        ctx["form"] = form_class

        return render(request, self.template_name, ctx)


class AdminDashBoard(LoginRequiredMixin, TemplateView):
    template_name = "accounts/detail/dashboard.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super(AdminDashBoard, self).get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(AdminDashBoard, self).get_context_data(**kwargs)
        ctx["title"] = "Dashboard"

        return ctx

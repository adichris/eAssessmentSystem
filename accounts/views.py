from django.views.generic import CreateView, DetailView
from .forms import UserCreateForm, StudentLoginForm, User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import resolve_url, redirect, reverse, render
from django.utils.http import is_safe_url
# from eAssessmentSystem.tool_utils import get_http_forbidden_response


class StaffCreateView(CreateView):
    model = User
    template_name = "accounts/create/superuser_createview.html"
    form_class = UserCreateForm

    def form_valid(self, form):
        valid_ = super(StaffCreateView, self).form_valid(form)
        login(self.request, self.object)
        self.object.is_admin = True
        self.object.save()
        return valid_


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

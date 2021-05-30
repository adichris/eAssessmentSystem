from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import resolve_url


class LandingPage(TemplateView):
    template_name = "home/landing page.html"

    def get_context_data(self, **kwargs):
        from .forms import StudentLoginForm
        ctx = super(LandingPage, self).get_context_data(**kwargs)
        ctx["student_login_form"] = StudentLoginForm(self.request.POST or None)
        return ctx


class AdminStaffLogin(LoginView):
    template_name = "home/genericLogin.html"

    def get_success_url(self):
        return resolve_url("landing-page")

    def get_context_data(self, **kwargs):
        ctx = super(AdminStaffLogin, self).get_context_data(**kwargs)
        ctx["admin_required"] = self.request.session.get("admin_required")
        return ctx

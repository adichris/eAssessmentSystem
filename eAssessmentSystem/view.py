from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import resolve_url, redirect
from django.utils.http import is_safe_url


class LandingPage(TemplateView):
    template_name = "home/landing page.html"

    def get_context_data(self, **kwargs):
        from .forms import StudentLoginForm
        ctx = super(LandingPage, self).get_context_data(**kwargs)
        ctx["student_login_form"] = StudentLoginForm(self.request.POST or None)
        ctx["include_footer"] = True
        return ctx


class AdminStaffLogin(LoginView):
    template_name = "home/genericLogin.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("landing-page")
        else:
            return super(AdminStaffLogin, self).get(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url and is_safe_url(next_url, self.request.get_host()):
            return next_url
        return resolve_url("landing-page")

    def get_context_data(self, **kwargs):
        ctx = super(AdminStaffLogin, self).get_context_data(**kwargs)
        ctx["admin_required"] = self.request.session.get("admin_required")
        return ctx


class Developer:
    def __init__(self, phone, **kwargs):
        self.__dict__.update(**kwargs)
        from phonenumber_field.phonenumber import PhoneNumber
        self.phone = PhoneNumber(national_number=phone, country_code="+233")


class AboutTemplatePage(TemplateView):
    template_name = "home/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "about"
        ctx["include_footer"] = True
        ctx["developers"] = self.get_developers()
        return ctx

    def get_developers(self):
        return (
            Developer(name="Addai Christopher", email="addaichristopher1@gmail.com", phone="0247128518", location="Sunyani"),
            Developer(name="Fosu Kwame Paul", email="wisdomp863@gmail.com", phone="0554308246 ", location="Sunyani"),
            Developer(name="Attakorah Bernard", email="----------", phone="0556653210", location="Sunyani"),
        )


class SupportTemplatePage(TemplateView):
    template_name = "home/support.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Support and Help"
        #ctx["include_footer"] = True
        return ctx



from eAssessmentSystem.tool_utils import is_safe_url
from accounts.models import User
from django.shortcuts import reverse, redirect
from django.views.generic import CreateView, UpdateView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import GeneralSetting
from .forms import GeneralSettingUpdateForm


class GeneralSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = GeneralSetting
    form_class = GeneralSettingUpdateForm
    template_name = "settings/create.html"

    def get_context_data(self, **kwargs):
        ctx = super(GeneralSettingUpdateView, self).get_context_data(**kwargs)
        ctx["title"] = "General  Settings"
        return ctx


class GeneralSettingCreateView(LoginRequiredMixin, CreateView):
    model = GeneralSetting
    form_class = GeneralSettingUpdateForm
    template_name = "settings/create.html"

    def get_user(self):
        try:
            user_id = self.kwargs.get("user_id")
            user_slug = self.kwargs.get("user_slug")
            user = User.objects.get(id=user_id, slug=user_slug)
            return user
        except User.DoesNotExist:
            return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super(GeneralSettingCreateView, self).get_context_data(**kwargs)
        user = self.get_user()
        name = "Your" if self.request.user == user else str(user.get_short_name()) + "'s"
        ctx["title"] = "%s General Settings" % name
        return ctx

    def form_valid(self, form):
        user = self.get_user()
        try:
            instance = GeneralSetting.objects.get(user_id=user.id)
            return redirect(instance.get_absolute_url())
        except GeneralSetting.DoesNotExist:
            form.instance.user = user
            
        return super(GeneralSettingCreateView, self).form_valid(form)

    # def form_invalid(self, form):
    #     returns = super(GeneralSettingCreateView, self).form_invalid(form)
    #     return returns

    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if is_safe_url(next_url, self.request.get_host()):
            return next_url
        return super().get_success_url()


class GeneralSettingDetailView(LoginRequiredMixin, DetailView):
    template_name = "settings/detail.html"
    model = GeneralSetting

    def get_context_data(self, **kwargs):
        ctx = super(GeneralSettingDetailView, self).get_context_data(**kwargs)
        ctx["title"] = "General  Settings"
        return ctx


class SettingRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            return reverse("setting:detail", kwargs=dict(pk=self.request.user.generalsetting.id,
                            user_id=self.request.user.generalsetting.user_id))
        except AttributeError:
            return reverse("setting:create")


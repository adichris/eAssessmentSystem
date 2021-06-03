from django.shortcuts import reverse, redirect
from django.views.generic import CreateView, UpdateView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import GeneralSetting
from .forms import GeneralSettingCreateForm, GeneralSettingUpdateForm


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
    form_class = GeneralSettingCreateForm
    template_name = "settings/create.html"

    def get_context_data(self, **kwargs):
        ctx = super(GeneralSettingCreateView, self).get_context_data(**kwargs)
        ctx["title"] = "General  Settings"
        return ctx

    def form_valid(self, form):
        try:
            instance = GeneralSetting.objects.get(user_id=self.request.user.id)
            return redirect(instance.get_absolute_url())
        except GeneralSetting.DoesNotExist:
            form.instance.user = self.request.user
            return super(GeneralSettingCreateView, self).form_valid(form)

    def form_invalid(self, form):
        returns = super(GeneralSettingCreateView, self).form_invalid(form)
        print(form.errors)
        return returns


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

from django.shortcuts import render, get_object_or_404, redirect
from .models import LectureModel
from .forms import LectureCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView, ListView
from accounts.forms import UserCreateForm
from eAssessmentSystem.tool_utils import admin_required_message


class LectureCreateView(LoginRequiredMixin, View):
    model = LectureModel
    lecture_form_class = LectureCreateForm
    profile_form = UserCreateForm
    template_name = "lecture/add.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            ctx = {
                "lecture_form":self.lecture_form_class(),
                "profile_form":self.profile_form(),
                "pageTitle": "Add Lecture"
            }
            return render(request, template_name=self.template_name, context=ctx)
        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:admin-login-page")

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            lecture_form = self.lecture_form_class(request.POST)
            profile_form = self.profile_form(request.POST)
            if lecture_form.is_valid() and profile_form.is_valid():
                profile_ins = profile_form.save(False)
                profile_ins.is_lecture = True
                profile_ins.save()
                lecture_ins = lecture_form.save(False)
                lecture_ins.profile = profile_ins
                lecture_ins.save()
                request.session["lecture_created_pk"] = lecture_ins.pk
                return redirect("lecture:created")
            ctx = {
                "lecture_form": lecture_form,
                "profile_form": profile_form,
                "pageTitle": "Add Lecture"
            }
            return render(request, self.template_name, ctx)


@login_required
def lecture_created_view(request):
    lecture_pk = request.session.get("lecture_created_pk")
    if request.user.is_staff and lecture_pk:
        lecture = get_object_or_404(LectureModel, pk=lecture_pk)
        ctx = {
            "lecture": lecture
        }
        # del request.session["lecture_created_pk"]
        return render(request, "lecture/created.html", ctx)
    return redirect("landing-page")


class LectureDetailView(LoginRequiredMixin, DetailView):
    model = LectureModel
    template_name = "lecture/detail.html"


class LectureListView(LoginRequiredMixin, ListView):
    model = LectureModel
    template_name = "lecture/list.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(LectureListView, self).get(request, *args, **kwargs)

        else:
            request.session["admin_required"] = admin_required_message(request.user)
            return redirect("accounts:admin-login-page")

    def get_context_data(self, object_list=None, **kwargs):
        ctx = super(LectureListView, self).get_context_data(object_list=object_list, **kwargs)
        ctx["query"] = self.request.GET.get("query")
        return ctx

    def get_queryset(self):
        query = self.request.GET.get("query")
        if query:
            return self.model.objects.search(query)
        else:
            return super(LectureListView, self).get_queryset().filter(profile__is_active=True)

from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user
from eAssessmentSystem.tool_utils import admin_required_message, get_http_forbidden_response


class RecordsView(LoginRequiredMixin, TemplateView):
    template_name = "record/all_records.html"

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_lecture:
            return super(RecordsView, self).get(request, *args, **kwargs)
        else:
            request.session["admin_required"] = admin_required_message(user)
            return redirect("accounts:student_login")


class StudentRecordTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "record/student.html"

    def get_student(self):
        return get_user(self.request).student

    def get(self, request, *args, **kwargs):
        student = self.get_student()

        if student and student.programme:
            return super(StudentRecordTemplateView, self).get(request, *args, **kwargs)
        else:
            return get_http_forbidden_response()

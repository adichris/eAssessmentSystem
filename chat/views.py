from accounts.models import User
from django.shortcuts import get_object_or_404, reverse, render
from django.views.generic import CreateView, ListView, DetailView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Message, CourseGroupMessage, CourseModel, CourseLevel
from .forms import MessageCreateForm, MessageCreateInlineForm, CourseMessageCreationForm
from django.utils.http import is_safe_url
from student.models import Student
from eAssessmentSystem.tool_utils import get_not_allowed_render_response, get_back_url
from django.db.models import ObjectDoesNotExist


class MessagesCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "chat/message/createview.html"
    form_class = MessageCreateForm

    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if next_url and is_safe_url(next_url, self.request.get_host()):
            return next_url
        return reverse("chat:individualchats_user", kwargs={"current_user_slug": self.get_to_user().slug})
    
    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_user = self.get_to_user()
        return super().form_valid(form)

    def get_to_user(self):
        return get_object_or_404(
            klass=User,
            slug=self.kwargs.get("to_user_slug")
            )

    def get_context_data(self, **kwargs):
        ctx = super(MessagesCreateView, self).get_context_data(**kwargs)
        ctx["title"] = "Send message"
        ctx["to_user"] = self.get_to_user()
        ctx["back_url"] = self.get_back_url()
        return ctx

    def get_back_url(self):
        back_url = self.request.GET.get("back")
        if back_url and is_safe_url(back_url, self.request.get_host()):
            return back_url
    
    def get_initial(self):
        initial = super().get_initial()
        initial["from_user"] = self.request.user
        initial["to_user"] = self.get_to_user()
        return initial

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return super(MessagesCreateView, self).get(request, *args, **kwargs)
        return get_not_allowed_render_response(request)

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return super(MessagesCreateView, self).post(request, *args, **kwargs)
        return get_not_allowed_render_response(request)


class ChatHistoryRedirectView(LoginRequiredMixin, RedirectView):
    model = Message

    def post(self, *args, **kwargs):
        try:
            to_user = User.objects.get(slug=self.kwargs.get("to_user_slug"))
        except User.DoesNotExist:
            pass
        else:
            self.model.objects.create(
                from_user_id=self.request.user.id,
                to_user_id=to_user.id,
                message=self.request.POST.get("message")
            )
        finally:
            return super(ChatHistoryRedirectView, self).post(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next")


class ChatTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "chat/home.html"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return super(ChatTemplateView, self).get(request, *args, **kwargs)

        return get_not_allowed_render_response(request)


class IndividualChatsTemplateView(LoginRequiredMixin, ListView):
    template_name = "chat/individual/chats.html"
    model = Message
    form_class = MessageCreateInlineForm

    def get_queryset(self):
        try:
            c_user_slug = self.kwargs.get("current_user_slug")
            self.current_user_msg = User.objects.get(slug=c_user_slug)
            return Message.objects.all_for_both(from_user=self.request.user, to_user=self.current_user_msg)
        except User.DoesNotExist:
            self.current_user_msg = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "All Individual Chats"
        ctx["current_user"] = self.current_user_msg
        ctx["form"] = self.form_class()
        try:
            ctx["lectures_contact"] = self.get_lecture_contact()
        except ObjectDoesNotExist:
            pass

        if not self.request.user.is_staff:
            ctx["students"] = self.get_students_contact()

        ctx["contactSearch"] = self.get_contact_query()
        return ctx
    
    def get_lecture_contact(self):
        from lecture.models import LectureModel
        returns = LectureModel.objects.filter(
            profile__is_active=True,
            coursemodel__level__student=self.request.user.student
        ).distinct()
        user = self.request.user
        if user.is_staff:
            return returns
        elif user.is_lecture:

            return returns.filter(department=user.lecturemodel.department).exclude(profile_id=user.id)
        try:
            return returns.filter(department__programme=user.student.programme)
        except Student.DoesNotExist:
            pass

    def get_contact_query(self):
        return self.request.GET.get("contactSearch")

    def get_students_contact(self):

        user = self.request.user
        contact_search = self.get_contact_query()
        if user.is_lecture:
            return Student.objects.search_lecture_student(contact_search, user.lecturemodel).filter(
                level=self.kwargs.get("level_pk"),
                programme_id=self.kwargs.get("programme_id"),
            )

        try:
            stu = user.student
            return Student.objects.search(contact_search).filter(
                    programme=stu.programme,
                    level=stu.level
                ).exclude(profile_id=self.request.user)
        except Student.DoesNotExist:
            pass


class CourseMassageChat(LoginRequiredMixin, DetailView):
    template_name = "chat/group/chat.html"
    message_form_class = CourseMessageCreationForm
    
    def get_context_data(self, **kwargs):
        ctx = super(CourseMassageChat, self).get_context_data(**kwargs)
        ctx["back_url"] = get_back_url(self.request)
        ctx["messages"] = self.get_messages()
        ctx["chat_form"] = self.message_form_class()
        ctx["title"] = "Chat Course Student"
        ctx["course_code"] = self.object.course.code
        return ctx

    def get_object(self, queryset=None):
        instance, created = CourseGroupMessage.objects.get_or_create(course_id=self.kwargs["course_id"])
        self.object = instance
        return instance

    def get_messages(self):
        instance = self.get_object()
        return instance.coursemessage_set.all()

    def get(self, request, *args, **kwargs):
        try:
            return super(CourseMassageChat, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)

    def post(self, request, *args, **kwargs):
        course_instance = self.get_object()
        ctx = self.get_context_data()
        ctx["object"] = course_instance
        try:
            form_instance = self.message_form_class(request.POST)
            if form_instance.is_valid():
                instance = form_instance.save(False)
                instance.group = course_instance
                instance.sender = request.user
                instance.save()
            else:
                ctx["chat_form"] = form_instance

            return render(request, self.template_name, ctx)
        except ObjectDoesNotExist:
            return get_not_allowed_render_response(request)


class ChatPeopleTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "chat/group/people.html"

    def init_instance(self):
        self.course_instance = get_object_or_404(CourseModel, code=self.kwargs["course_code"])

    def get_context_data(self, **kwargs):
        ctx = super(ChatPeopleTemplateView, self).get_context_data(**kwargs)
        ctx["title"] = "Chatting People"
        ctx["course_name"] = self.course_instance.name
        ctx["lecture_profile"] = self.course_instance.lecture.profile
        ctx["students"] = self.course_instance.programme.student_set.all()
        ctx["back_url"] = get_back_url(self.request)
        return ctx

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            self.init_instance()
            return super(ChatPeopleTemplateView, self).get(request, *args, **kwargs)
        return get_not_allowed_render_response(request)


class SelectedDepartmentProgrammeLevel(LoginRequiredMixin, TemplateView):
    template_name = "chat/individual/selection.html"

    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_staff:
                return super(SelectedDepartmentProgrammeLevel, self).get(request, *args, **kwargs)
            else:
                pass
        except ObjectDoesNotExist:
            pass
        return get_not_allowed_render_response(request)

    def get_context_data(self, **kwargs):
        ctx = super(SelectedDepartmentProgrammeLevel, self).get_context_data(**kwargs)
        ctx["title"] = "Select Department Programme and Level"
        ctx["programmes"] = self.get_programme()
        ctx["levels"] = self.get_levels()
        return ctx

    def get_programme(self):
        return self.request.user.lecturemodel.department.programme_set.all()

    def get_levels(self):
        return CourseLevel.objects.all().distinct()


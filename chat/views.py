from accounts.models import User
from django.shortcuts import get_object_or_404, resolve_url, reverse
from django.views.generic import CreateView, ListView, DetailView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Message, GroupMessage, GrpMsg, GroupMessageToChoices
from .forms import MessageCreateForm, MessageCreateInlineForm, MessageGroupCreateForm, GrpMsgCreateInlineForm
from django.utils.http import is_safe_url
from student.models import Student
from django.http import HttpResponse, HttpRequest
from typing import Any, Dict
from eAssessmentSystem.tool_utils import get_not_allowed_render_response


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
        if self.request.user.is_staff:
            ctx["staff_contact"] = self.get_staff_contact()
        ctx["lectures_contact"] = self.get_lecture_contact()

        if not self.request.user.is_staff:
            ctx["students"] = self.get_students_contact()
        return ctx
    
    def get_lecture_contact(self):
        from lecture.models import LectureModel
        returns =  LectureModel.objects.filter(
            profile__is_active=True,
        )
        user = self.request.user
        if user.is_staff:
            return returns
        elif user.is_lecture:

            return returns.filter(department=user.lecturemodel.department).exclude(profile_id=user.id)
        try:
            return returns.filter(department__programme=user.student.programme)
        except Student.DoesNotExist:
            pass

    def get_students_contact(self):
        students =  Student.objects.filter(
            profile__is_active=True
        )
        user = self.request.user
        try:
            stu = user.student
            return students.filter(programme=stu.programme, level=stu.level).exclude(profile_id=self.request.user)
        except Student.DoesNotExist:
            pass
        
        if user.is_lecture:
            return students.filter(programme__department=user.lecturemodel.department)

    def get_staff_contact(self):
        return User.objects.get_staffs().exclude(id=self.request.user.id)

    
class GroupChatListView(LoginRequiredMixin, ListView):
    template_name = "chat/group/chat.html"
    model = GroupMessage

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "group chat"
        ctx["messages"] = self.get_all_grp_chat()
        try:
            ctx["current_grp"] = self.grp_instance
        except AttributeError:
            pass
        ctx["form"] = self.get_message_form()
        return ctx
    
    def get_message_form(self):
        return GrpMsgCreateInlineForm()
    
    def get_all_grp_chat(self):
        try:
            self.grp_instance = self.model.objects.get(
                pk=self.request.GET.get("grppk"),
                to_group=self.request.GET.get("togrp"),
            )
            return self.grp_instance.grpmsg_set.all()
        except GroupMessage.DoesNotExist:
            return None


class GroupMsgCreateView(LoginRequiredMixin, CreateView):
    model = GrpMsg
    fields = ("message", )

    def form_valid(self, form):
        form.instance.group = self.group_instance
        return super().form_valid(form)
    
    def init_instances(self):
        self.group_instance = get_object_or_404(
            GroupMessage,
            pk=self.kwargs.get("msg_grp_pk"),
            from_user_id=self.request.user.id
        )
    
    def get(self, request, *args: str, **kwargs):
        self.init_instances()
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args: str, **kwargs):
        self.init_instances()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if next_url is not None and is_safe_url(next_url, self.request.get_host()):
            return next_url
        return super().get_success_url()


class MessageGroupCreateView(LoginRequiredMixin, CreateView):
    template_name = "chat/group/create.html"
    model = GroupMessage
    form_class = MessageGroupCreateForm

    def form_valid(self, form,) -> HttpResponse:
        form.instance.from_user = self.request.user
        return super().form_valid(form)
    
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        user = request.user
        if user.is_staff or user.is_lecture:
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        user = request.user
        if user.is_staff or user.is_lecture:
            return super().post(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs =  super().get_form_kwargs()
        kwargs["user_obj"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Add New Message Group"
        return ctx

    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if next_url is not None and is_safe_url(next_url, self.request.get_host()):
            return next_url        
        return resolve_url("chat:group_chats")


class GroupMessageDetailView(LoginRequiredMixin, DetailView):
    model = GroupMessage
    template_name = "chat/group/detail.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user == self.get_object().from_user:
            return super().get(request, *args, **kwargs)
        else:
            return get_not_allowed_render_response(request)
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            group_name=self.kwargs.get("grpname"),
            id=self.kwargs.get("grpid")
        )
    
    def get_context_data(self, **kwargs) -> Dict:
        ctx = super(GroupMessageDetailView, self).get_context_data(**kwargs)
        ctx["title"] = "%s Chats Group Details" % self.object
        ctx["all_msg_cnt"] = self.get_total_msgs()
        return ctx

    def get_total_msgs(self):
        #TODO implement get total messages in a group
        return "not implemented ⚠"
    
    def get_group_members(self):
        # TODO return a group members queryset
        """
        Check group constraints and apply it on users; return user who pass
        """
        is_students = self.object.to_group == GroupMessageToChoices.STUDENTS
        is_lecture = self.object.to_group == GroupMessageToChoices.LECTURES
        is_staffs = self.object.to_group == GroupMessageToChoices.STAFFS
        is_all = self.object.to_group == GroupMessageToChoices.ALL
        members = None
        if is_students:
            programme = None
            level = None
            department = None
        elif is_lecture:
            department = None

        elif is_staffs:
            return User.objects.filter(is_active=True)

        elif is_all:
            return User.objects.filter(is_active=True)


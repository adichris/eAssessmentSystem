from accounts.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Message
from .forms import MessageCreateForm, MessageCreateInlineForm
from django.utils.http import is_safe_url
from student.models import Student


class MessagesCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "chat/message/createview.html"
    form_class = MessageCreateForm

    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if next_url and is_safe_url(next_url, self.request.get_host()):
            return next_url
        return super().get_success_url()
    
    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_user = self.get_to_user()
        return super().form_valid(form)
    
    def get_to_user(self):
        return get_object_or_404(
            klass=User,
            slug=self.kwargs.get("to_user_slug")
            )
    
    def get_success_url(self) -> str:
        next_url = self.request.GET.get("next")
        if is_safe_url(next_url, self.request.get_host()):
            return next_url
        return super().get_success_url()
    
    def get_initial(self):
        initial =  super().get_initial()
        initial["from_user"] = self.request.user
        initial["to_user"] = self.get_to_user()
        return initial
    

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
        ctx =  super().get_context_data(**kwargs)
        ctx["title"] = "All Individual Chats"
        ctx["current_user"] = self.current_user_msg
        ctx["form"] = self.form_class()
        if self.request.user.is_staff:
            ctx["staff_contact"] = self.get_staff_contact()
        ctx["lectures_contact"] = self.get_lecture_contact()

        if not self.request.user.is_staff:
            ctx["students"] = self.get_students_contact()
            print(ctx["students"])
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
    model = Message

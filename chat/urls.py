from .views import (
    MessagesCreateView, ChatTemplateView, IndividualChatsTemplateView,
    GroupChatListView
    )
from django.urls import path


app_name = "chat"
urlpatterns = [
    path("add/message<slug:to_user_slug>", MessagesCreateView.as_view(), name="add_message"),
    path("", ChatTemplateView.as_view(), name="home"),
    path("individualschats/", IndividualChatsTemplateView.as_view(), name="individual_chats"),
    path("groupchats/", GroupChatListView.as_view(), name="group_chats"),
    path("individualchats/<slug:current_user_slug>/", IndividualChatsTemplateView.as_view(), name="individualchats_user"),
]
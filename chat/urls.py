from .views import (
    MessagesCreateView, ChatTemplateView, IndividualChatsTemplateView,
    GroupChatListView, MessageGroupCreateView, GroupMsgCreateView,
    GroupMessageDetailView,
    )
from django.urls import path


app_name = "chat"
urlpatterns = [
    path("add/message<slug:to_user_slug>", MessagesCreateView.as_view(), name="add_message"),
    path("", ChatTemplateView.as_view(), name="home"),
    path("individualschats/", IndividualChatsTemplateView.as_view(), name="individual_chats"),
    path("individualchats/<slug:current_user_slug>/", IndividualChatsTemplateView.as_view(), name="individualchats_user"),
    path("groupchatdetails/<str:grpname>/<int:grpid>", GroupMessageDetailView.as_view(), name="group_detail"),
    path("groupchats/", GroupChatListView.as_view(), name="group_chats"),
    path("groupchats/<int:msg_grp_pk>/", GroupMsgCreateView.as_view(), name="group_msg_create"),
    path("groupchats/add", MessageGroupCreateView.as_view(), name="group_chat_create"),
]
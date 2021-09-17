from .views import (
    MessagesCreateView, ChatTemplateView, IndividualChatsTemplateView,
    ChatHistoryRedirectView, CourseMassageChat, ChatPeopleTemplateView,
    SelectedDepartmentProgrammeLevel,
    )
from django.urls import path


app_name = "chat"
urlpatterns = [
    path("start/messaging<slug:to_user_slug>", MessagesCreateView.as_view(), name="start_message"),
    path("add/message<slug:to_user_slug>", ChatHistoryRedirectView.as_view(), name="add_message"),
    path("", ChatTemplateView.as_view(), name="home"),
    path("individualschats/", IndividualChatsTemplateView.as_view(), name="individual_chats"),
    path("individualschats/<int:programme_id>/<int:level_pk>", IndividualChatsTemplateView.as_view(), name="individual_chats4lecture"),
    path("individualchats/<slug:current_user_slug>/", IndividualChatsTemplateView.as_view(), name="individualchats_user"),
    path("individualchats/<slug:current_user_slug>/<int:programme_id>/<int:level_pk>", IndividualChatsTemplateView.as_view(), name="individualchats_user_4lecture"),
    path("course/<int:course_id>/", CourseMassageChat.as_view(), name="course_message"),
    path("course/people/<str:course_code>/", ChatPeopleTemplateView.as_view(), name="course_people"),
    path("individualselection/", SelectedDepartmentProgrammeLevel.as_view(), name="individual_filter_selection"),
]

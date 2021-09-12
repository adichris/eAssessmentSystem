from .views import (StudentCreateView, SuccessfulStudentRegistration, StudentListView, StudentDetailView,
                    LectureStudentsListView, HODStudentTemplateView, ProgrammeLevelStudentTemplateView
                    )
from django.urls import path

app_name = "student"
urlpatterns = [
   path("register/", StudentCreateView.as_view(), name="register"),
   path("registered/", SuccessfulStudentRegistration.as_view(), name="registered"),
   path("list/", StudentListView.as_view(), name="list"),
   path("list/lectureStudent/", LectureStudentsListView.as_view(), name="listLectureStudent"),
   path("detail/<int:pk>/", StudentDetailView.as_view(), name="detail"),

    # hod
    path("hod/group/", HODStudentTemplateView.as_view(), name="group_4_hod"),
    path("hod/group/<int:level_id>/<int:programme_id>", ProgrammeLevelStudentTemplateView.as_view(), name="programme_level_4_hod"),
]

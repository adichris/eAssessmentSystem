from .views import StudentCreateView, SuccessfulStudentRegistration, StudentListView, StudentDetailView, LectureStudentsListView
from django.urls import path

app_name = "student"
urlpatterns = [
   path("register/", StudentCreateView.as_view(), name="register"),
   path("registered/", SuccessfulStudentRegistration.as_view(), name="registered"),
   path("list/", StudentListView.as_view(), name="list"),
   path("list/lectureStudent/", LectureStudentsListView.as_view(), name="listLectureStudent"),
   path("detail/<int:pk>/", StudentDetailView.as_view(), name="detail"),
]

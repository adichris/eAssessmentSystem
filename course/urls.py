from django.urls import path
from .views import (
    CourseCreateView, CourseDetailView, CourseDeleteView,
    CourseUpdateView, LectureCourseListView, CourseAssignmentView,
    CourseUnassignmentView,
)


app_name = "course"
urlpatterns = [
    path("add/", CourseCreateView.as_view(), name="add"),
    path("<str:courseName>/<int:pk>/", CourseDetailView.as_view(), name="detail"),
    path("delete/<str:courseName>/<int:pk>/<int:course_programme_pk>", CourseDeleteView.as_view(), name="delete"),
    path("update/<str:courseName>/<int:pk>/", CourseUpdateView.as_view(), name="update"),
    path("lecturecourses/", LectureCourseListView.as_view(), name="for_lecturer"),
    path("lecturecourses/bbhod/<int:lecturer_pk>/", LectureCourseListView.as_view(), name="lecturer_courses"),

    # hod and admin
    path("assignment/forlecturer/<int:lecturer_pk>/", CourseAssignmentView.as_view(), name="assigment"),
    path("unassignment/fromlecturer/<str:course_code>/", CourseUnassignmentView.as_view(),
         name="unassignment")

]

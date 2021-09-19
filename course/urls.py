from django.urls import path
from .views import (
    CourseCreateView, CourseDetailView, CourseDeleteView,
    CourseUpdateView, LectureCourseListView, CourseAssignmentView,
    CourseUnassignmentView, SelectCourseToChatInView, LevelCreateView, LevelListViewView,
    LevelDetailView, LevelUpdateView, LevelDeleteView
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
         name="unassignment"),
    path("selecttochat/", SelectCourseToChatInView.as_view(), name="select_to_chat"),

    # level
    path("level/listall/", LevelListViewView.as_view(), name="level_list"),
    path("level/addnewone/", LevelCreateView.as_view(), name="level_add"),
    path("level/detail/<int:pk>", LevelDetailView.as_view(), name="level_detail"),
    path("level/update/<int:pk>", LevelUpdateView.as_view(), name="level_update"),
    path("level/delete/<int:pk>", LevelDeleteView.as_view(), name="level_delete"),

]

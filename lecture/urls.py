from django.urls import path
from .views import LectureCreateView, LectureDetailView, lecture_created_view, LectureListView

app_name = "lecture"
urlpatterns = [
    path("add/", LectureCreateView.as_view(), name="add"),
    path("created/", lecture_created_view, name="created"),
    path("detail/<int:pk>/", LectureDetailView.as_view(), name="detail"),
    path("list/", LectureListView.as_view(), name="list"),
]

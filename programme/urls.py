from django.urls import path, include
from .views import ProgrammeCreateView, ProgrammeDetailView, ProgrammeUpdateView

app_name = "programme"

urlpatterns = [
    path("addto/<str:departmentName>/<int:departmentPK>/", ProgrammeCreateView.as_view(), name="add"),
    path("<str:programName>/<int:pk>/", ProgrammeDetailView.as_view(), name="detail"),
    path("edit/<str:programName>/<int:pk>/", ProgrammeUpdateView.as_view(), name="update"),
    path("course/", include("course.urls")),

]

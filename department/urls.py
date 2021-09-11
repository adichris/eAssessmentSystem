from django.urls import path, include
from .views import (
    DepartmentCreateView, DepartmentDetailView, DepartmentGridView,
    StudentDepartmentTemplateView, HodStatusUpdateView, HodDashboardTemplateView
)


app_name = "department"
urlpatterns = [
    path("create/", DepartmentCreateView.as_view(), name="create"),
    path("detail/<str:name>/<int:pk>/", DepartmentDetailView.as_view(), name="detail"),
    path("listall/", DepartmentGridView.as_view(), name="list"),
    path("programme/", include("programme.urls")),
    path("student/", StudentDepartmentTemplateView.as_view(), name="student_programme"),

    path("changeorsethod/<str:name>/<int:pk>/", HodStatusUpdateView.as_view(), name="change-hod"),
    path("hoddashboard/", HodDashboardTemplateView.as_view(), name="hod-dashboard"),

]

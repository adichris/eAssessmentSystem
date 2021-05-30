from django.urls import path
from .views import RecordsView, StudentRecordTemplateView


app_name = "records"

urlpatterns = [
    path("all/", RecordsView.as_view(), name="all"),
    path("student/", StudentRecordTemplateView.as_view(), name="student"),

]

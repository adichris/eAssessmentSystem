from django.urls import path
from .views import StaffCreateView, UserDetailView, StaffLoginView, AdminLoginView, user_logout, student_login
from eAssessmentSystem.view import AdminStaffLogin

app_name = "accounts"

urlpatterns = [
    path("login/staff", StaffLoginView.as_view(), name="staff-login-page"),
    path("login/admin", AdminLoginView.as_view(), name="admin-login-page"),
    path("logout", user_logout, name="logout"),
    path("profile/<slug:slug>/<int:pk>/", UserDetailView.as_view(), name="user-profile"),
    path("login/", AdminStaffLogin.as_view(), name="loginPage"),
    path("add/staff/", StaffCreateView.as_view(), name="staff-add"),
    path("studentLogin/", student_login, name="student_login"),
]

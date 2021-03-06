from django.urls import path
from .views import (AdminCreateView, UserDetailView, StaffLoginView,
                    AdminLoginView, user_logout, student_login, AddAdminView,
                    UserUpdateView, ConfirmPasswordResetView, ChangePasswordView,
                    ChangePasswordUpdateView, AdminDashBoard
 )
from eAssessmentSystem.view import AdminStaffLogin


app_name = "accounts"

urlpatterns = [
    path("login/staff", StaffLoginView.as_view(), name="staff-login-page"),
    path("login/admin", AdminLoginView.as_view(), name="admin-login-page"),
    path("logout", user_logout, name="logout"),
    path("addAdminWarning", AddAdminView.as_view(), name="add_admin_view"),
    path("profile/<slug:slug>/<int:pk>/", UserDetailView.as_view(), name="user-profile"),
    path("editprofile/<slug:slug>/<int:pk>/", UserUpdateView.as_view(), name="profile_edit"),
    path("login/", AdminStaffLogin.as_view(), name="loginPage"),
    path("addadmin/", AdminCreateView.as_view(), name="admin-add"),
    path("studentLogin/", student_login, name="student_login"),

    path("resetpassword/", ConfirmPasswordResetView.as_view(), name="confirm_reset_pwd"),
    path("changepwdreset/", ChangePasswordView.as_view(), name="change_pwd_reset"),

    path("changeyourpwd/", ChangePasswordUpdateView.as_view(), name="change_pwd_update"),

    path("dashboard/", AdminDashBoard.as_view(), name="admin-dashboard"),
]

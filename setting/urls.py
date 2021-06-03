from django.urls import path
from .views import GeneralSettingCreateView, GeneralSettingUpdateView, GeneralSettingDetailView, SettingRedirectView
app_name = "setting"

urlpatterns = [
    path("redirect/", SettingRedirectView.as_view(), name="redirect"),
    path("create/", GeneralSettingCreateView.as_view(), name="create"),
    path("update/<int:user_id>/<int:pk>/", GeneralSettingUpdateView.as_view(), name="update"),
    path("detail/<int:user_id>/<int:pk>/", GeneralSettingDetailView.as_view(), name="detail"),
]

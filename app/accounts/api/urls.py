from django.urls import path
from accounts.api.views import UserRegisterView,ProfileView,UpdateMobileView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("update-mobile/", UpdateMobileView.as_view(), name="update_mobile"),
    path("profile/", ProfileView.as_view(), name="profile"),


]

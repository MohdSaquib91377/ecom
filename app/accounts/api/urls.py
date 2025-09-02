from django.urls import path,include
from accounts.api.views import UserRegisterView,ProfileView,UpdateMobileView,AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('addresses',
 AddressViewSet, basename='address')

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("update-mobile/", UpdateMobileView.as_view(), name="update_mobile"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('', include(router.urls)),


]

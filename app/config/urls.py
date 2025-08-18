from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

schema_view = get_schema_view(
    openapi.Info(
        title="OTP API",
        default_version="v1",
        description="API documentation for OTP authentication system",
        terms_of_service="https://yourdomain.com/terms/",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/otp/", include("otp.api.urls")),  # include OTP urls here
    path("api/accounts/", include("accounts.api.urls")),  # include Accounts urls here
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/token/", include("tokens.api.urls")),

]

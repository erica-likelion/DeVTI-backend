"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.permissions import AllowAny

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter

schema_view = get_schema_view(
    openapi.Info(title="DevTI API", default_version="v1", description="DevTI 화이팅!!"),
    public=True,
)


class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    permission_classes = [AllowAny]


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    permission_classes = [AllowAny]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui("swagger")),
    path("api/matching/", include("matchings.matching.urls")),
    path("api/room/", include("matchings.room.urls")),
    path("api/profile/", include("users.profile.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/auth/kakao/", KakaoLogin.as_view(), name="kakao_login"),
    path("api/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("accounts/", include("allauth.urls")),
]

from django.urls import path
from .views import DashboardAPIView

urlpatterns = [
    path("", DashboardAPIView.as_view(), name="dashboard-api"),
]

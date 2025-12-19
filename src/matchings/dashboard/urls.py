from django.urls import path
from .views import DashboardAPIView

urlpatterns = [
    path("<int:room_id>/", DashboardAPIView.as_view(), name="dashboard-api"),
]

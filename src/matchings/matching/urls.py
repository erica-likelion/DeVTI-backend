from django.urls import path
from .views import MatchingView, carrot_control_view, wagging_control_view

urlpatterns = [
    path("<int:room_id>/", MatchingView.as_view()),
    path("carrot/", carrot_control_view),
    path("wagging/", wagging_control_view),
]

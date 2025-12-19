from django.urls import path
from .views import MatchingView, carrot_control_view, wagging_control_view, wagging_start_view

urlpatterns = [
    path("carrot/<int:participant_id>/", carrot_control_view),
    path("wagging/", wagging_control_view),
    path("<int:room_id>/wagging-start/", wagging_start_view),
    path("<int:room_id>/", MatchingView.as_view()),
]

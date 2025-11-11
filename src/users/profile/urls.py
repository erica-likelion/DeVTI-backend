from django.urls import path
from .views import ProfileView, DevtiView, participant_profile_view

urlpatterns = [
    path("", ProfileView.as_view()),
    path("devti/", DevtiView.as_view()),
    path("<int:participant_id>/", participant_profile_view),
]

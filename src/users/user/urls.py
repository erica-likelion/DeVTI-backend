from django.urls import path
from .views import get_carrot_users, get_room_users, delete_participant

urlpatterns = [
    path("<int:room_id>/", get_room_users),
    path("carrot/<int:room_id>/", get_carrot_users),
    path("participant/<int:participant_id>/", delete_participant),
]

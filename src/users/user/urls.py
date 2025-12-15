from django.urls import path
from .views import get_carrot_users, get_room_users

urlpatterns = [
    path("<int:room_id>/", get_room_users),
    path("carrot/<int:room_id>/", get_carrot_users),
]

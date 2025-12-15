from django.urls import path
from .views import get_carrot_users, get_room_users

urlpatterns = [
    path("", get_room_users),
    path("carrot/", get_carrot_users),
]

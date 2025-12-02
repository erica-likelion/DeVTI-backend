from django.urls import path
from .views import (
    RoomView,
    RoomDetailView,
    room_join_view,
    validate_code_view,
    room_join_admin_view,
)

urlpatterns = [
    path("", RoomView.as_view()),
    path("<int:room_id>/", RoomDetailView.as_view()),
    path("validate-code/", validate_code_view),
    path("join/", room_join_view),
    path("join-admin/", room_join_admin_view),
]

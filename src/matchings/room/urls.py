from django.urls import path
from .views import RoomView, participate_view

urlpatterns = [path("", RoomView.as_view()), path("participate/", participate_view)]

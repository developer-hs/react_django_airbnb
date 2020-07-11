from rest_framework.routers import DefaultRouter
from django.urls import path
from . import viewsets

router = DefaultRouter()
router.register("", viewsets.RoomViewset, basename="room")

app_name = "rooms"

urlpatterns = router.urls

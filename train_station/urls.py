from django.urls import path, include
from rest_framework import routers

from train_station.views import StationViewSet, RouteViewSet, TrainTypeViewSet, TrainViewSet, CrewViewSet, \
    JourneyViewSet

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("crew", CrewViewSet)
router.register("journeys", JourneyViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"

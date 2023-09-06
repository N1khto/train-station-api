from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from train_station.models import Station
from train_station.permissions import IsAdminOrIfAuthenticatedReadOnly
from train_station.serializers import StationSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)



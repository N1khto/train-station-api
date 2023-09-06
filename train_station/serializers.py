from rest_framework import serializers

from train_station.models import Station


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude",)

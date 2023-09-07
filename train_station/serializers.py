from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from train_station.models import Station, Route, TrainType, Train, Crew, Journey, Ticket, Order


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "train_type", "carriage_num", "places_in_carriage", "capacity", "image")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class CrewListSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name")


class CrewDetailSerializer(CrewSerializer):
    journeys = serializers.SlugRelatedField(many=True, read_only=True, slug_field="info")

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name", "journeys")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(JourneySerializer):
    route = serializers.SlugRelatedField(many=False, read_only=True, slug_field="route")
    crew = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")
    train = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "tickets_available", "departure_time", "arrival_time", "crew")


class JourneyDetailSerializer(JourneySerializer):
    source = StationSerializer(many=False, read_only=True, source="route.source")
    destination = StationSerializer(many=False, read_only=True, source="route.destination")
    distance = serializers.SlugRelatedField(many=False, read_only=True, source="route", slug_field="distance")
    train = TrainSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "source", "destination", "distance", "train", "tickets_available", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["carriage"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "carriage", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

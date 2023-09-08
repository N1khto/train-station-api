import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        related_name="source_routes",
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        related_name="destination_routes",
    )
    distance = models.PositiveSmallIntegerField()

    @property
    def route(self):
        return f"{self.source.name} - {self.destination.name}"

    @staticmethod
    def validate_route(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise(
                {
                    "destination": "source and destination "
                                   "can't be the same place"
                }
            )

    def clean(self):
        Route.validate_route(self.source, self.destination, ValidationError)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Route, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return self.route


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "crew"


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def train_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/trains/", filename)


class Train(models.Model):
    name = models.CharField(max_length=255)
    carriage_num = models.PositiveSmallIntegerField()
    places_in_carriage = models.PositiveSmallIntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.SET_NULL, null=True, related_name="trains"
    )
    image = models.ImageField(null=True, upload_to=train_image_path)

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return self.carriage_num * self.places_in_carriage


class Journey(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        Train, on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    @property
    def info(self):
        return f"{str(self.route)} at {str(self.departure_time)}"

    def __str__(self):
        return self.info

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    carriage = models.PositiveSmallIntegerField()
    seat = models.PositiveSmallIntegerField()

    @staticmethod
    def validate_ticket(carriage, seat, journey, error_to_raise):
        for ticket_attr_value, ticket_attr_name, journey_attr_name in [
            (carriage, "carriage", "carriage_num"),
            (seat, "seat", "places_in_carriage"),
        ]:
            count_attrs = getattr(journey, journey_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1 to {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.carriage,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (f"{str(self.journey)} "
                f"(carriage: {self.carriage}, seat: {self.seat})")

    class Meta:
        unique_together = ("journey", "carriage", "seat")
        ordering = ["carriage", "seat"]

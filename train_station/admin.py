from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Train, TrainType, Station, Route, Crew, Journey, Order, Ticket


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)


admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Ticket)

admin.site.unregister(Group)

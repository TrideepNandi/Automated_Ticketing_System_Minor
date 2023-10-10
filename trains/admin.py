from django.contrib import admin
from . models import *
# Register your models here.

class DaysAdmin (admin.ModelAdmin):
    model = Days
    list_display = ['choice']

class StationAdmin (admin.ModelAdmin):
    model = Station
    list_display = ['station_code', 'station_name']
    
class TrainClassAdmin (admin.ModelAdmin):
    model = TrainClass
    list_display = ['class_code', 'coach_prefix', 'class_name']
    
class TrainDetailsAdmin (admin.ModelAdmin):
    model = TrainDetails
    list_display = ['train_code', 'distance' , 'train_name' , 'start_time', 'duration', 'end_time']
    
class ViaDetailsAdmin (admin.ModelAdmin):
    model = ViaDetails
    list_display = ['relative_pos', 'station_name', 'for_train']
    
class SeatAvailabilityAdmin (admin.ModelAdmin):
    model = SeatAvailability
    list_display = ['train', 'classes', 'fare_per_passenger', 'total_seats', 'booked_seats', 'waiting_list', ]
    
class FareAdmin (admin.ModelAdmin):
    model = Fare
    list_display = ['train', 'station', 'train_class', 'fare_amount',]
    
    
class TicketReservationAdmin (admin.ModelAdmin):
    model = TicketReservation
    list_display = ['PNR_no' ,'from_station', 'to_station', 'reservation_time', 'from_date', 'total_fare']
    
    
admin.site.register(Days, DaysAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(TrainClass, TrainClassAdmin)
admin.site.register(TrainDetails, TrainDetailsAdmin)
admin.site.register(ViaDetails,ViaDetailsAdmin)
admin.site.register(SeatAvailability,SeatAvailabilityAdmin)
admin.site.register (Fare, FareAdmin)
admin.site.register (TicketReservation, TicketReservationAdmin)
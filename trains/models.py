from django.db import models

class Days(models.Model):
    choice = models.CharField(max_length=20)

    def __str__(self):
        return self.choice


class Station(models.Model):
    station_code = models.CharField(max_length=10, primary_key=True)
    station_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.station_code} {self.station_name}"


class TrainClass(models.Model):
    class_code = models.CharField(max_length=3)
    coach_prefix = models.CharField(max_length=3)
    class_name = models.CharField(max_length=50)
    seat_per_coach = models.IntegerField()
    
    def __str__(self):
        return self.class_name

class TrainDetails(models.Model):
    train_code = models.CharField(primary_key=True, max_length=5)
    distance = models.IntegerField(null=False, blank=False)
    train_name = models.CharField(max_length=50)
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    duration = models.DurationField()
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    classes = models.ManyToManyField(TrainClass)
    running_days = models.ManyToManyField(Days)
    route = models.ManyToManyField(Station, through='ViaDetails')
    
    def __str__(self):
        return self.train_code
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Set the total_seats from TrainClass
        for train_class in self.classes.all():
            total_seats = train_class.seat_per_coach

        # Create or update Fare and Se  atAvailability instances
        for station in self.route.all():
            for train_class in self.classes.all():
                try:
                    # Try to retrieve an existing Fare instance
                    fare = Fare.objects.get(train=self, station=station, train_class=train_class)
                except Fare.DoesNotExist:
                    # If it doesn't exist, create a new one
                    fare = Fare(train=self, station=station, train_class=train_class)   
                    # Set fare_amount for the Fare instance
                    fare.fare_amount = 0  # Set the initial fare amount here
                fare.save()

                try:
                    # Try to retrieve an existing SeatAvailability instance
                    seat_availability = SeatAvailability.objects.get(train=self, classes=train_class)
                except SeatAvailability.DoesNotExist:
                    # If it doesn't exist, create a new one
                    seat_availability = SeatAvailability(train=self, classes=train_class)
                    seat_availability.fare_per_passenger = 0  # Set the initial fare per passenger here
                    seat_availability.total_seats = total_seats  # Set the total seats available for booking
                seat_availability.save()
                
class ViaDetails(models.Model):
    relative_pos = models.IntegerField()
    station_name = models.ForeignKey(Station, on_delete=models.PROTECT)
    for_train = models.ForeignKey(TrainDetails, on_delete=models.PROTECT)
    
class SeatAvailability(models.Model):
    train = models.ForeignKey(TrainDetails, on_delete=models.PROTECT)
    classes = models.ForeignKey(TrainClass, on_delete=models.PROTECT, related_name="train_class_seat")
    fare_per_passenger = models.IntegerField()
    total_seats = models.IntegerField()  # Total seats available for booking
    booked_seats = models.IntegerField(default=0)  # Number of booked seats
    waiting_list = models.IntegerField(default=0)  # Number of passengers in the waiting list

    def __str__(self):
        return f"{self.fare_per_passenger} {self.booked_seats}"
    
class Fare(models.Model):
    train = models.ForeignKey(TrainDetails, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    train_class = models.ForeignKey(TrainClass, on_delete=models.CASCADE)
    fare_amount = models.DecimalField(max_digits=10, decimal_places=2)


class TicketReservation(models.Model):
    CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer Not to Say'),
    )
    train = models.ForeignKey(TrainDetails, on_delete=models.PROTECT)  # Reference the TrainDetails model
    train_class = models.ForeignKey(TrainClass, on_delete=models.PROTECT)  # Reference the TrainClass model
    PNR_no = models.CharField(primary_key=True, max_length=18)
    from_station = models.OneToOneField(Station, on_delete=models.PROTECT, related_name="from_station_r")
    to_station = models.OneToOneField(Station, on_delete=models.PROTECT, related_name="to_station_r")
    reservation_time = models.DateTimeField(auto_now=True)
    from_date = models.DateField(auto_now=True)
    total_fare = models.IntegerField()
    passenger_name = models.CharField(max_length=30)
    passenger_age = models.IntegerField()
    passenger_sex = models.CharField(max_length=20, choices=CHOICES)
    ticket_status = models.CharField(max_length=5)
    ticket_seat_no = models.IntegerField(null=True, blank=True)


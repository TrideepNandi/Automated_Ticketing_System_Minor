# Create your views here.
from pickle import NONE
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.views import View
from django.utils import timezone
from trains.models import TrainDetails,SeatAvailability, Fare, ViaDetails
from trains.forms import TrainSearchForm


class SearchTrainView(View):
    template_name = 'trains/search_train.html'

    def get(self, request):
        # Render an empty search form
        form = TrainSearchForm()
        return render(request, self.template_name, {
            'form' : form
            })

    def post(self, request):
        # Get the user input from the form
        form = TrainSearchForm(request.POST)
        from_station = request.POST.get('from_station')
        to_station = request.POST.get('to_station')
        date_of_journey = request.POST.get('date_of_journey')

        print(from_station , to_station, date_of_journey)
        
        request.session['from_station'] = from_station
        request.session['to_station'] = to_station
        request.session['date_of_journey'] = date_of_journey
        request.session.save()
        # Translate the date_input to a day of the week (e.g., Monday)
        date_obj = timezone.datetime.strptime(date_of_journey, '%Y-%m-%d')
        day_of_week = date_obj.strftime('%A')
        print(day_of_week)
        
        # Query the database to find matching trains
        matching_trains = TrainDetails.objects.filter(
            route__station_code=from_station,
        ).filter(
            route__station_code=to_station,
        ).filter(
            running_days__choice__icontains=day_of_week
        )
        
        if matching_trains.exists():
            #return HttpResponseBadRequest("No matching trains found")

            # List to store any invalid station selections
            invalid_station_selections = []

            # Iterate through each matching train
            for train in matching_trains:
                try:
                    from_station_pos = ViaDetails.objects.get(for_train=train, station_name=from_station).relative_pos
                    to_station_pos = ViaDetails.objects.get(for_train=train, station_name=to_station).relative_pos
                except ViaDetails.DoesNotExist:
                    invalid_station_selections.append(train.train_code)
                    continue

                # Check if from_station_pos is less than to_station_pos
                if from_station_pos >= to_station_pos:
                    invalid_station_selections.append(train.train_code)

            # If there are any invalid station selections, return a bad request response
            if invalid_station_selections:
                matching_trains = None
                context = {
                    'from_station_code': from_station,
                    'to_station_code': to_station,
                    'date_of_journey': date_of_journey,
                    'matching_trains': matching_trains,
                    'form' : form,
                }
            else:
            # Create a list to store seat availability for each train class
                seat_availability_data = []
                fare_data = []
                for train in matching_trains:
                    for train_class in train.classes.all():
                        try:
                            fare = self.calculate_fare(train, train_class, from_station, to_station)
                            seat_availability = SeatAvailability.objects.get(train=train, classes=train_class)
                            available_seats = seat_availability.total_seats - seat_availability.booked_seats
                        except SeatAvailability.DoesNotExist:
                            seat_availability = None
                        except Fare.DoesNotExist:
                            fare = None
                        
                        seat_availability_data.append({
                            'train': train,
                            'train_class': train_class,
                            'available_seats': available_seats,
                        })
                
                        fare_data.append({
                            'train': train,
                            'train_class': train_class,
                            'fare': fare,
                        })
            
                context = {
                    'from_station_code': from_station,
                    'to_station_code': to_station,
                    'date_of_journey': date_of_journey,
                    'matching_trains': matching_trains,
                    'seat_availability_data': seat_availability_data,
                    'fare_data' : fare_data,
                    'form' : form,
                }
        else:
            matching_trains = None
            context = {
                'from_station_code': from_station,
                'to_station_code': to_station,
                'date_of_journey': date_of_journey,
                'matching_trains': matching_trains,
                'form' : form,
            }
        print(matching_trains)
        return render(request, self.template_name, context)
    
    def calculate_fare(self, train, train_class, from_station, to_station):
        try:
            # Retrieve fare amounts for the 'from_station' and 'to_station' based on the train and class
            from_station_fare = Fare.objects.get(train=train, station=from_station, train_class=train_class).fare_amount
            to_station_fare = Fare.objects.get(train=train, station=to_station, train_class=train_class).fare_amount

            # Calculate the fare as the difference between 'to_station_fare' and 'from_station_fare'
            fare = to_station_fare - from_station_fare

            return fare

        except Fare.DoesNotExist:
            # Handle the case where fare information is not found
            return None  # You can return an appropriate value or raise an exception

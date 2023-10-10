from django.views import View
from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from trains.models import TrainDetails, TrainClass, SeatAvailability, Fare, TicketReservation, Station
import random
from datetime import datetime
from trains.forms import BookSeatForm
from django.db import transaction

   

class BookSeatView(View):
    template_name = 'trains/book_seat.html'

    def get(self, request, train_code, class_code):
        try:
            form = BookSeatForm()
            train = TrainDetails.objects.get(train_code=train_code)
            train_class = TrainClass.objects.get(class_code=class_code)
            from_station_session = request.session.get('from_station')
            to_station_session = request.session.get('to_station')
            from_station = Station.objects.get(station_code = from_station_session)
            to_station = Station.objects.get(station_code = to_station_session)
            date_of_journey = request.session.get('date_of_journey')
            return render(request, self.template_name, {'train': train, 'form' : form, 'from_station' : from_station, 'to_station': to_station, 'date_of_journey': date_of_journey, 'selected_class': train_class})
        
        except TrainDetails.DoesNotExist:
            return HttpResponse('Train not found.')
        except TrainClass.DoesNotExist:
            return HttpResponse('Train class not found.')

    
    @transaction.atomic
    def post(self, request, train_code, class_code):
        try:
            form = BookSeatForm(request.POST)
            train = TrainDetails.objects.get(train_code=train_code)
            train_class = TrainClass.objects.get(class_code=class_code)
            seat_availability = SeatAvailability.objects.get(train=train, classes=train_class)
            from_station_session = request.session.get('from_station')
            to_station_session = request.session.get('to_station')
            from_station = Station.objects.get(station_code = from_station_session)
            to_station = Station.objects.get(station_code = to_station_session)
            fare = self.calculate_fare(train, train_class, from_station_session, to_station_session)

            form = BookSeatForm(request.POST)
            if form.is_valid():
                if seat_availability.total_seats > seat_availability.booked_seats:
                    # Seat available, book it
                
                    passenger_name=request.POST.get('passenger_name'),
                    passenger_age_str = request.POST.get('passenger_age')
                    try:
                        passenger_age = int(passenger_age_str)
                    except ValueError:
                        # Handle the case where passenger_age is not a valid integer
                        #return HttpResponse('Invalid passenger age. Please enter a valid age.')
                        print(type(passenger_age))

                    passenger_sex=request.POST.get('passenger_sex'),
                    ticket_status='CNF'  # Initially set as confirmed

                    # Update SeatAvailability
                    seat_availability.booked_seats += 1
                    seat_availability.save()

                    # Create a TicketReservation for confirmed passengers
                    ticket_reservation = TicketReservation(
                        train = train,
                        train_class = train_class,
                        PNR_no=self.generate_pnr(),
                        from_station=from_station,
                        to_station=to_station,
                        total_fare=fare,
                        passenger_name=passenger_name,
                        passenger_age=passenger_age,
                        passenger_sex=passenger_sex,
                        ticket_status=ticket_status,
                    )
                    ticket_reservation.save()

                    #return HttpResponse(f'Seat booked with PNR: {ticket_reservation.PNR_no}') #add the redirect for the train confirmation
                    # Redirect to the search page
                    return HttpResponseRedirect("/search-train/")
                
                else:
                    # Seat not available, add to waiting list
                    passenger_name=request.POST.get('passenger_name'),
                    passenger_age=request.POST.get('passenger_age'),
                    passenger_sex=request.POST.get('passenger_sex'),
                    ticket_status='WL{0}'.format(seat_availability.waiting_list + 1)  # Calculate WL number

                    # Update SeatAvailability's waiting list count
                    seat_availability.waiting_list += 1
                    seat_availability.save()

                    # Retrieve "from station" and "to station" from the session
            
                    # Create a TicketReservation
                    ticket_reservation = TicketReservation(
                        train = train,
                        train_class = train_class,
                        PNR_no=self.generate_pnr(),  # Define a function to generate unique PNR
                        from_station=from_station,  # Set the first station as from station
                        to_station=to_station,  # Set the last station as to station
                        total_fare=seat_availability.fare_per_passenger,
                        passenger_name=passenger_name,
                        passenger_age=passenger_age,
                        passenger_sex=passenger_sex,
                        ticket_status=ticket_status  # Initially set as confirmed
                    )
                    ticket_reservation.save()
                    #return HttpResponse('Seat not available. Added to the waiting list.')
                    # Redirect to the search page
                    return HttpResponseRedirect("/search-train/")
            
            else:
                # Form is not valid, re-render the form with errors
                return render(request, self.template_name, {'train': train, 'seat_availability': seat_availability, 'form': form})
            
        except TrainDetails.DoesNotExist:
            return HttpResponse('Train not found.')
        except TrainClass.DoesNotExist:
            return HttpResponse('Train class not found.')

    def generate_pnr(self):
        # Get the current date and time
        current_datetime = datetime.now()

        # Format the date and time as a string (e.g., "20231007154322" for October 7, 2023,15:43:22)
        formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")

        # Generate a random 4-digit number
        random_number = random.randint(1000, 9999)

        # Combine the formatted date/time and random number to create the PNR
        pnr = f"{formatted_datetime}{random_number}"

        return pnr
    
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

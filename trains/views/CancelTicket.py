from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from trains.models import SeatAvailability, TicketReservation
from trains.forms import CancelTicketForm
from django.db import transaction

"""
class CancelTicketView(View):
    template_name = 'trains/cancel_ticket.html'

    def get(self, request, pnr):
        try:
            ticket = TicketReservation.objects.get(PNR_no=pnr)
            form = CancelTicketForm()
            return render(request, self.template_name, {'ticket': ticket, 'form' : form})
        except TicketReservation.DoesNotExist:
            return render(request, self.template_name, {'error_message': 'Ticket not found.'})

    def post(self, request, pnr):
        try:
            ticket = TicketReservation.objects.get(PNR_no=pnr)
            form = CancelTicketForm(request.POST)
            # Check if the ticket is confirmed (CNF) or in the waiting list (WL)
            if ticket.ticket_status.startswith('CNF'):
                # If the ticket is confirmed, cancel it and update SeatAvailability
                seat_availability = SeatAvailability.objects.get(train=ticket.train, classes=ticket.train_class)
                seat_availability.booked_seats -= 1
                seat_availability.save()
            
            #Delete the ticket
            ticket.delete()
            
            # Handle waiting list upgrades if applicable
            if ticket.ticket_status.startswith('WL'):
                self.handle_waiting_list_upgrades(ticket.train, ticket.train_class, int(ticket.ticket_status[2:]))


            return redirect('ticket_status', pnr=pnr)
        except TicketReservation.DoesNotExist:
           return render(request, self.template_name, {'error_message': 'Ticket not found.', 'form': form})

    def handle_waiting_list_upgrades(self, train, train_class,canceled_wl_number):
        # Get all passengers in the waiting list for the same train and train class
        waiting_list_passengers = TicketReservation.objects.filter(
            train=train,
            train_class=train_class,
            ticket_status__startswith='WL'
       ).order_by('ticket_status')  # Order by WL number

        for ticket in waiting_list_passengers:
            # Update the ticket's status from WL to CNF based on seat availability
            seat_availability = SeatAvailability.objects.get(train=ticket.train, classes=ticket.train_class)
            if seat_availability.booked_seats < seat_availability.total_seats:
                ticket.ticket_status = 'CNF'
                ticket.save()
                
                # Update SeatAvailability
                seat_availability.booked_seats += 1
                seat_availability.waiting_list -= 1
                seat_availability.save()
                
            elif(seat_availability.booked_seats > seat_availability.total_seats):
                for waiting_list_ticket in waiting_list_passengers:
                    canceled_wl_number += 1
                    waiting_list_ticket.ticket_status = f'WL{canceled_wl_number}'
                    waiting_list_ticket.save()

            for ticket in waiting_list_passengers:
                 ticket.save()
            
            else:
                # If no more seats are available, break the loop
                break
"""

class CancelTicketView(View):
    @transaction.atomic    
    def get(self, request, pnr):
        try:
            ticket = TicketReservation.objects.get(PNR_no=pnr)
            ticket = TicketReservation.objects.get(PNR_no=pnr)
            form = CancelTicketForm(request.POST)
            # Check if the ticket is confirmed (CNF) or in the waiting list (WL)
            if ticket.ticket_status.startswith('CNF'):
                # If the ticket is confirmed, cancel it and update SeatAvailability
                seat_availability = SeatAvailability.objects.get(train=ticket.train, classes=ticket.train_class)
                seat_availability.booked_seats -= 1
                seat_availability.save()
            
            #Delete the ticket
            ticket.ticket_status = 'Cancelled'
            
            # Handle waiting list upgrades if applicable
            if ticket.ticket_status.startswith('WL'):
                self.handle_waiting_list_upgrades(ticket.train, ticket.train_class, int(ticket.ticket_status[2:]))

            ticket.save()

            return redirect('pne_status')
        except TicketReservation.DoesNotExist:
            return redirect('pnr_status')  # Redirect back to the PNR status page
        except TicketReservation.DoesNotExist:
            # Handle the case where the ticket with the given PNR does not exist
            return redirect('pnr_status')  # Redirect back to the PNR status page with an error message
        
    def handle_waiting_list_upgrades(self, train, train_class,canceled_wl_number):
        # Get all passengers in the waiting list for the same train and train class
        waiting_list_passengers = TicketReservation.objects.filter(
            train=train,
            train_class=train_class,
            ticket_status__startswith='WL'
       ).order_by('ticket_status')  # Order by WL number

        for ticket in waiting_list_passengers:
            # Update the ticket's status from WL to CNF based on seat availability
            seat_availability = SeatAvailability.objects.get(train=ticket.train, classes=ticket.train_class)
            if seat_availability.booked_seats < seat_availability.total_seats:
                ticket.ticket_status = 'CNF'
                ticket.save()
                
                # Update SeatAvailability
                seat_availability.booked_seats += 1
                seat_availability.waiting_list -= 1
                seat_availability.save()
                
            elif(seat_availability.booked_seats > seat_availability.total_seats):
                for waiting_list_ticket in waiting_list_passengers:
                    canceled_wl_number += 1
                    waiting_list_ticket.ticket_status = f'WL{canceled_wl_number}'
                    waiting_list_ticket.save()

            for ticket in waiting_list_passengers:
                 ticket.save()
            
            else:
                # If no more seats are available, break the loop
                break

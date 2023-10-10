from django.shortcuts import render
from django.views import View
from django.shortcuts import render
from django.views import View
from django.shortcuts import render
from trains.models import TicketReservation
from trains.forms import PNRStatusForm

class CheckPNRStatusView(View):
    template_name = 'trains/pnr_status.html'

    def get(self, request):
            form = PNRStatusForm()        
            return render(request, self.template_name, {'form' : form})

    def post (self, request):
        form = PNRStatusForm(request.POST)
        pnr = request.POST.get ("pnr")
        
        if form.is_valid():
            try:
                ticket = TicketReservation.objects.get(PNR_no=pnr)
            except TicketReservation.DoesNotExist:
                ticket = None
            print(ticket)
            return render(request, self.template_name, {'ticket': ticket, 'form': form})
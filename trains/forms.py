from django import forms
from .models import Station, TicketReservation

class TrainSearchForm(forms.Form):
    from_station = forms.ModelChoiceField(queryset=Station.objects.all(), label="From Station: ")
    to_station = forms.ModelChoiceField(queryset=Station.objects.all(), label="To Station: ")
    date_of_journey = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
class BookSeatForm(forms.ModelForm):
    passenger_name = forms.CharField(label='Passenger Name', max_length=30)
    passenger_age = forms.IntegerField(label='Passenger Age')
    passenger_sex = forms.ChoiceField(label='Passenger Sex', choices=(
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer Not to Say'),
    ))
    """class Meta:
        model = TicketReservation
        fields = ['passenger_name', 'passenger_age', 'passenger_sex']"""

class PNRStatusForm(forms.Form):
    pnr = forms.CharField(label='PNR Number', max_length=18)

class CancelTicketForm(forms.Form):
    pnr = forms.CharField(label='PNR Number', max_length=18)

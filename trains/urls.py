from django.urls import path
from .views.BookSeat import BookSeatView
from .views.SearchTrain import SearchTrainView
from .views.CancelTicket import CancelTicketView
from .views.CheckPNR import CheckPNRStatusView

urlpatterns = [
    # URL for the Search Train View
    path('search-train/', SearchTrainView.as_view(), name='search_train'),

    # URL for the Book Seat View (replace 'train_code' and 'class_code' with actual parameters)
    path('book-seat/<str:train_code>/<str:class_code>/', BookSeatView.as_view(), name='book_seat'),

    # URL for the Cancel Ticket View (replace 'pnr' with the actual parameter)
    path('cancel-ticket/<str:pnr>/', CancelTicketView.as_view(), name='cancel_ticket'),

    # URL for the Check PNR Status View (replace 'pnr' with the actual parameter)
    path('pnr-status/', CheckPNRStatusView.as_view(), name='pnr'),

]

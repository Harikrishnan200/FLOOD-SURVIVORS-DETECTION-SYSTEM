from django.urls import path
from . import views

urlpatterns = [
   path('receive_gps_data/', views.receive_gps_data, name='receive_gps_data'),
   path('print_user/', views.print_user, name='print_user'),
   path('get_location_data/', views.get_location_data, name='get_location_data'),

]

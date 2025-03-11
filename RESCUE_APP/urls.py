from django.urls import path
from . import views

urlpatterns = [

    path('dashboard/', views.rescue_dashboard, name='rescue_dashboard'),
    path('update_rescue_details/<int:id>/', views.update_rescue_details, name='update_rescue_details'),
    path('update_rescue_table/', views.update_rescue_table, name='update_rescue_table'),
    path('update_complete_and_pending/<int:id>', views.update_complete_and_pending, name='update_complete_and_pending'),

]

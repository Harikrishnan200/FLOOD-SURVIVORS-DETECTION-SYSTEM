from django.urls import path
from . import views

urlpatterns = [

    path('dashboard/', views.rescue_dashboard, name='rescue_dashboard'),

]

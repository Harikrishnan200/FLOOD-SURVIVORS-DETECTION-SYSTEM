from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('video_feed/', views.video_feed, name='video_feed'),
   

]

from django.urls import path
from . import views

urlpatterns = [

    path('recent_data/', views.get_recent_data, name='recent_data'),
    path('download/<int:video_id>/', views.download_video, name='download_video'),


]

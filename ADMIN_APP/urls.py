from django.urls import path
from . import views
from UPLOAD_VIDEO_APP.views import handle_file_upload 


urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('upload_video/', handle_file_upload, name='upload_video'),
    path('previous_data/', views.previous_data, name='previous_data'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('get_unique_person_count/', views.get_unique_person_count, name='get_unique_person_count'),

    

]

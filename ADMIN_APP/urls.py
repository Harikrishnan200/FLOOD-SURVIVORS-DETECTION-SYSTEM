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
    path('add_users/', views.add_users, name='add_users'),
    path('add_users/<str:email>/', views.add_users, name='add_users_with_email'),
    path('update_rescue_team_member/<str:email>/', views.update_rescue_team_member, name='update_user'),
    path('delete_rescue_team_member/<str:email>/', views.delete_rescue_team_member, name='delete_user'),
    path('update_rescue_team_table_content/', views.update_rescue_team_table_content, name='update_rescue_team_table_content'),
    path('admin_details/', views.admin_details, name='admin_details'),
]

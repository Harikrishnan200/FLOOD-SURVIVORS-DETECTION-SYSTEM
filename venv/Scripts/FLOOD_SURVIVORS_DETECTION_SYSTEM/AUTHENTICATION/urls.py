from django.urls import path
from . import views

urlpatterns = [
    path('', views.userLogin, name='user_login'),
    path('create_account/', views.userRegister, name='create_account'),

]

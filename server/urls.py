
from django.contrib import admin
from django.urls import path
from server import views
urlpatterns = [
    path('user', views.user_list),
    path('auth', views.get_token),
]


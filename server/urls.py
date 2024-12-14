
from django.contrib import admin
from django.urls import path
from server import views
urlpatterns = [
    path('user', views.user),
    path('login', views.login),
    path('post', views.post),
    path('like', views.like),
    # path('post/<int>', views.post_detail),
]


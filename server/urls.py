
from django.contrib import admin
from django.urls import path
from server import views
urlpatterns = [
    path('user', views.user),
    path('login', views.login),
    path('post', views.post),
    path('like', views.like),
    path('follow', views.follow),
    path('feed', views.feed),
    path('isfollowing', views.is_following),
    path('isliked', views.is_liked),
    # path('post/<int>', views.post_detail),
]


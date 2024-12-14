from django.http import HttpResponse, HttpRequest, JsonResponse

from server.models import User, Post, Like
from server.permissions import IsOwnerOrReadOnly

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework import permissions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userid', 'username', 'avatar', 'bio', 'createdAt', 'editedAt']
        
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['postid', 'userid', 'caption', 'image', 'likes_no', 'createdAt', 'editedAt']
        

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['likeid', 'userid', 'postid', 'createdAt']
        

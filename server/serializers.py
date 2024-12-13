from django.http import HttpResponse, HttpRequest, JsonResponse
from rest_framework import serializers
from server.models import User
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userid', 'username', 'password', 'avatar', 'bio', 'createdAt', 'editedAt']
        
        
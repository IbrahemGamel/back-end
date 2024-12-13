from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from server.models import User
from server.serializers import UserSerializer
from hashlib import sha256
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

@api_view(['POST'])
def get_token(request):
    '''
    Gets the user token
    '''
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid() == False:
        try:
            user = User.objects.get(username=request.data.get('username'))
        except User.DoesNotExist:
            return Response({'error': 'Unable to log in with provided credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.password == request.data.get('password'):
            token = Token.objects.get(user=user)
            return Response({'token':token.key}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error': 'Unable to log in with provided credentials.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Unable to log in with provided credentials.'}, status=status.HTTP_400_BAD_REQUEST)
    
        

@api_view(['GET', 'POST'])
def user_list(request):
    '''
    List all users, or create a new user.
    '''
    
    if request.method == 'GET':
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
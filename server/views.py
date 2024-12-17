from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from server.models import User, Post, Like, Follow
from server.serializers import UserSerializer, PostSerializer, LikeSerializer, FollowSerializer

from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from hashlib import sha256        


@api_view(['GET', 'POST'])
def user(request):
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
            user = User.objects.get(username=request.data.get('username'))
            user.set_password(request.data.get('password'))
            user.save()
            token = Token.objects.get(user=user)
            
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data.get('username'))
    if not user.check_password(request.data.get('password')):
        return Response({'detail': 'No User matches the given query.'}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    
@api_view(['GET', 'POST', 'PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post(request):
    '''
    List all users posts, edit, or add a new post.
    '''
    
    if request.method == 'GET':
        userid = request.user.userid
        post = Post.objects.filter(userid=userid)
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data={
            'caption': request.data.get('caption'),
            'image': request.FILES.get('image'),
            'userid': request.user.pk
        }, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        postid = request.data.get('postid')
        post = get_object_or_404(Post, postid=postid)
        post.delete()
        return Response({'success': f'post {postid} has been deleted'}, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        ... # implemented in the next version

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_details(request):
    postid = request.data.get('postid')
    if postid:
        post = get_object_or_404(Post, pk=postid)
        likes = Like.objects.filter(postid=postid)
        serializer = PostSerializer(post)
        return Response({'post': serializer.data, 'likes': likes}, status=status.HTTP_200_OK)



@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def like(request):
    '''
    retrieve like(s), add a like, or deletes (one)
    '''
    
    if request.method == 'GET':
        postid = request.data.get('postid')
        if postid:
            likes = Like.objects.filter(postid=postid)
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Please provide postid in request body'}, status=status.HTTP_400_BAD_REQUEST)
            
        
    elif request.method == 'POST':
        data = request.data.copy()
        data['userid'] = request.user.pk
        print(data)
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            post = Post.objects.get(pk=data['postid'])
            post.likes_no += 1
            post.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        likeid = request.data.get('likeid')
        if likeid is None:
            return Response({'likeid': f'This field is necessary, provide it in request body'}, status=status.HTTP_200_OK)
            
        like = get_object_or_404(Like, likeid=likeid)
        like.postid.likes_no -= 1
        like.postid.save()
        like.delete()
        return Response({'success': f'like {request.data.get("likeid")} has been deleted'}, status=status.HTTP_200_OK)
        

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def like_details(request):
    likeid = request.data.get('likeid')
    postid = request.data.get('postid')
    if likeid and postid:
        return Response({'detail': 'Please provide either lilkeid or postid only'}, status=status.HTTP_200_OK)
        
    if likeid:
        post = get_object_or_404(Like, pk=likeid)
        serializer = LikeSerializer(instance=like)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def follow(request: HttpRequest):
    '''
    GET Follows, creates one and deletes one.
    '''
    if request.method == 'GET':
        userid = request.user.pk
        follows = Follow.objects.filter(follower=userid)
        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        data = request.data.copy()
        data['follower'] = request.user.pk
        serializer = FollowSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        followid = request.data.get('followid')
        follow = get_object_or_404(Follow, followid=followid)
        follow.delete()
        return Response({'success': f'follow {followid} has been deleted'}, status=status.HTTP_200_OK)
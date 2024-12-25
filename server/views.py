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
from drf_yasg.utils import swagger_auto_schema

from hashlib import sha256        


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import UserSerializer

@swagger_auto_schema(
    operation_description="Retrieve or create users",
    methods=['GET'],
    manual_parameters=[
        openapi.Parameter(
            name='username',
            in_=openapi.IN_QUERY,
            description="Filter by username (case-insensitive, partial match). Required for GET requests.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successful response for GET requests",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user."),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user."),
                        'bio': openapi.Schema(type=openapi.TYPE_STRING, description="Bio of the user."),
                        'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Avatar URL of the user."),
                    },
                ),
            ),
        ),
    },
)
@swagger_auto_schema(
    operation_description="Create a new user",
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user."),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="Password for the user."),
            'bio': openapi.Schema(type=openapi.TYPE_STRING, description="Optional bio for the user."),
            'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description="Optional avatar image for the user."),
        },
        required=['username', 'password'],
    ),
    responses={
        201: openapi.Response(
            description="Successful response for POST requests",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description="Auth token for the created user."),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user."),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user."),
                            'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Avatar URL of the user."),
                            'bio': openapi.Schema(type=openapi.TYPE_STRING, description="Bio of the user."),
                            'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was created."),
                            'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was last edited."),
                            'lastactive': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when user last seen."),

                            
                        },
                    ),
                },
            ),
        ),
        400: openapi.Response(description="Bad request (validation errors or missing parameters)."),
    }
)
@api_view(['GET', 'POST'])
def user(request):
    
    
    if request.method == 'GET':
        username = request.query_params.get('username')
        if not username:
            return Response({'detail': 'Parameter username is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username__icontains=username)
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['avatar'] = request.FILES.get('avatar')
        serializer = UserSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data.get('username'))
            user.set_password(request.data.get('password'))
            user.save()
            token = Token.objects.get(user=user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    operation_description="Authenticate a user and return a token.",
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="The username of the user."),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="The password of the user."),
        },
        required=['username', 'password'],
    ),
    responses={
        201: openapi.Response(
            description="Authentication successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description="The authentication token."),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user."),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user."),
                            'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Avatar URL of the user."),
                            'bio': openapi.Schema(type=openapi.TYPE_STRING, description="Bio of the user."),
                            'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was created."),
                            'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was last edited."),
                            'lastactive': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when user last seen."),
                        },
                    ),
                },
            ),
        ),
        404: openapi.Response(description="User not found or invalid password."),
        400: openapi.Response(description="Invalid input data."),
    }
)
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data.get('username'))
    if not user.check_password(request.data.get('password')):
        return Response({'detail': 'No User matches the given query.'}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retrieve all posts created by the userid provided.",
    manual_parameters=[
        openapi.Parameter(
            'userid',
            openapi.IN_QUERY,
            description="The ID of the authenticated user (optional). Defaults to the logged-in user.",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of user's posts",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the post."),
                        'caption': openapi.Schema(type=openapi.TYPE_STRING, description="Caption of the post."),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Image URL of the post."),
                        'likes_no': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of likes."),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Post creation timestamp."),
                        'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Last edited timestamp."),
                    },
                ),
            ),
        ),
    },
)
@swagger_auto_schema(
    methods=['POST'],
    operation_description="Create a new post.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'caption': openapi.Schema(type=openapi.TYPE_STRING, description="Caption of the post."),
            'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description="Image file for the post."),
        },
        required=['image'],
    ),
    responses={
        201: openapi.Response(
            description="Post created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the new post."),
                    'caption': openapi.Schema(type=openapi.TYPE_STRING, description="Caption of the post."),
                    'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Image URL of the post."),
                    'likes_no': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of likes."),
                    'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Post creation timestamp."),
                    'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Last edited timestamp."),
                },
            ),
        ),
        400: openapi.Response(description="Invalid input data."),
    },
)
@swagger_auto_schema(
    methods=['DELETE'],
    operation_description="Delete a user's post.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the post to delete."),
        },
        required=['postid'],
    ),
    responses={
        200: openapi.Response(
            description="Post deleted successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_STRING, description="Success message."),
                },
            ),
        ),
        404: openapi.Response(description="Post not found."),
    },
)
@swagger_auto_schema(
     methods=['PUT'],
    operation_description="Update an existing post. The user can update fields like caption and image.",
    request_body=PostSerializer,  # Specify the serializer for request validation
    responses={
        200: openapi.Response(
            description="Successfully updated the post.",
            schema=PostSerializer()
        ),
        400: openapi.Response(
            description="Invalid input.",
            examples={
                "application/json": {"caption": ["This field may not be blank."]}
            },
        ),
        404: openapi.Response(
            description="Post not found.",
            examples={
                "application/json": {"detail": "Not found."}
            },
        ),
    },
)
@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post(request):
    '''
    List all users posts, edit, or add a new post.
    '''
    
    if request.method == 'GET':
        userid = request.paramslist.get('userid') 
        userid = userid if userid else request.user.pk
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
        post = get_object_or_404(Post, postid=postid)
    
        serializer = PostSerializer(instance=post, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Retrieve the details of a specific post and its likes.",
    manual_parameters=[
        openapi.Parameter(
            'postid',
            openapi.IN_QUERY,
            description="The ID of the post to retrieve.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Post details and likes",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'post': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Details of the requested post",
                        properties={
                            'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the post."),
                            'caption': openapi.Schema(type=openapi.TYPE_STRING, description="Caption of the post."),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Image URL of the post."),
                            'likes_no': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of likes."),
                            'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Post creation timestamp."),
                            'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Last edited timestamp."),
                        },
                    ),
                    'likes': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'likeid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the like."),
                                'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who liked the post."),
                                'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of when the like was created."),
                            },
                        ),
                        description="List of likes for the post",
                    ),
                },
            ),
        ),
        404: openapi.Response(description="Post not found."),
        400: openapi.Response(description="Invalid request. `postid` is required."),
    },
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_details(request):
    postid = request.data.get('postid')
    if postid:
        post = get_object_or_404(Post, pk=postid)
        likes = Like.objects.filter(postid=postid)
        serializer = PostSerializer(post)
        return Response({'post': serializer.data, 'likes': likes}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retrieve likes for a specific post.",
    manual_parameters=[
        openapi.Parameter(
            'postid',
            openapi.IN_QUERY,
            description="The ID of the post to retrieve likes for.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of likes for the specified post.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'likeid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the like."),
                        'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who liked the post."),
                        'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the liked post."),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the like."),
                    },
                ),
            ),
        ),
        400: openapi.Response(description="Invalid request. `postid` is required."),
    },
)
@swagger_auto_schema(
    methods=['POST'],
    operation_description="Add a like to a specific post.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="The ID of the post to like."),
        },
        required=['postid'],
    ),
    responses={
        201: openapi.Response(
            description="Like added successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'likeid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the new like."),
                    'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who liked the post."),
                    'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the liked post."),
                    'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the like."),
                },
            ),
        ),
        400: openapi.Response(description="Invalid input data."),
    },
)
@swagger_auto_schema(
    methods=['DELETE'],
    operation_description="Delete a like by its ID.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'postid': openapi.Schema(type=openapi.TYPE_STRING, description="The ID of the post to unlike"),
        },
        required=['postid'],
    ),
    responses={
        200: openapi.Response(
            description="Like deleted successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_STRING, description="Success message."),
                },
            ),
        ),
        404: openapi.Response(description="Like not found."),
        400: openapi.Response(description="`postid` is required."),
    },
)
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def like(request):
    '''
    retrieve like(s), add a like, or deletes (one)
    '''
    
    if request.method == 'GET':
        postid = request.query_params.get('postid')
        if postid:
            likes = Like.objects.filter(postid=postid)
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Parameter postid is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
        
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
        postid = request.data.get('postid')
        if postid is None:
            return Response({'likeid': f'This field is necessary, provide it in request body'}, status=status.HTTP_200_OK)
            
        like = get_object_or_404(Like, userid=request.user.pk, postid=postid)
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


@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retrieve the list of users that the authenticated user is following.",
    responses={
        200: openapi.Response(
            description="List of users that the authenticated user is following.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'followid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the follow relationship."),
                        'follower': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the follower."),
                        'following': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user being followed."),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the follow relationship was created."),
                    },
                ),
            ),
        ),
        400: openapi.Response(description="No follows found for the authenticated user."),
    },
)
@swagger_auto_schema(
    methods=['POST'],
    operation_description="Create a follow relationship between the authenticated user and another user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'following': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="The ID of the user to follow."),
        },
        required=['following'],
    ),
    responses={
        201: openapi.Response(
            description="Follow created successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'followid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the new follow relationship."),
                    'follower': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the follower."),
                    'following': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user being followed."),
                    'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the follow relationship was created."),
                },
            ),
        ),
        400: openapi.Response(description="Invalid input data."),
    },
)
@swagger_auto_schema(
    methods=['DELETE'],
    operation_description="Delete a follow relationship by its ID.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'followid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="The ID of the follow relationship to delete."),
        },
        required=['followid'],
    ),
    responses={
        200: openapi.Response(
            description="Follow deleted successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_STRING, description="Success message."),
                },
            ),
        ),
        404: openapi.Response(description="Follow relationship not found."),
        400: openapi.Response(description="`followid` is required."),
    },
)
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
    

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retrieve the feed of posts from users that the authenticated user is following.",
    responses={
        200: openapi.Response(
            description="A list of posts from followed users.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user."),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user."),
                            'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Avatar URL of the user."),
                            'bio': openapi.Schema(type=openapi.TYPE_STRING, description="Bio of the user."),
                            'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was created."),
                            'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was last edited."),
                            'lastactive': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when user last seen."),
                            },
                        ),
                        'post': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the post."),
                            'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who created the post."),
                            'caption': openapi.Schema(type=openapi.TYPE_STRING, description="Caption of the post."),
                            'image': openapi.Schema(type=openapi.TYPE_STRING, description="URL of the post's image."),
                            'likes_no': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of likes on the post."),
                            'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was created."),
                            'editedAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp when the post was last edited."),
                            }
                        )
                    },
                ),
            ),
        ),
    },
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def feed(request: HttpRequest):
    followed_users = Follow.objects.filter(follower=request.user.pk).values_list('following', flat=True)
    posts = Post.objects.filter(userid__in=followed_users).order_by('-createdAt')
    serializer = PostSerializer(posts, many=True)
    print(serializer.data)
    return Response([{'user':UserSerializer(User.objects.get(pk=post['userid'])).data,'post':post} for post in serializer.data], status=status.HTTP_200_OK)

#test



@swagger_auto_schema(
    methods=['GET'],
    operation_description="Used to check if a user liked a post.",
    manual_parameters=[
        openapi.Parameter(
            'postid',
            openapi.IN_QUERY,
            description="The ID of the post to check like for.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
        openapi.Parameter(
            'userid',
            openapi.IN_QUERY,
            description="The ID of the user to check like for.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
    ],
    responses={
        200: openapi.Response(
            description="The like for the specified post.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'likeid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the like."),
                        'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who liked the post."),
                        'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the liked post."),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the like."),
                    },
                ),
            ),
        ),
        404: openapi.Response(description="Not found."),
    },
)
@api_view(['GET'])
def is_liked(request: HttpRequest):
    postid = request.query_params.get('postid')
    userid = request.query_params.get('userid')
    
    like = get_object_or_404(Like, postid=postid, userid=userid)
    serializer = LikeSerializer(like)
    return Response(serializer.data, status=status.HTTP_200_OK)



@swagger_auto_schema(
    methods=['GET'],
    operation_description="Used to check if a user is following another user.",
    manual_parameters=[
        openapi.Parameter(
            'followerid',
            openapi.IN_QUERY,
            description="The ID of the user to check if he is following the other user.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
        openapi.Parameter(
            'followingid',
            openapi.IN_QUERY,
            description="The ID of the user to check if he is followed by the first user.",
            type=openapi.TYPE_STRING,
            required=True,
            format=openapi.FORMAT_UUID,
        ),
    ],
    responses={
        200: openapi.Response(
            description="The Follow for the specified query.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'likeid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the like."),
                        'userid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the user who liked the post."),
                        'postid': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="UUID of the liked post."),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the like."),
                    },
                ),
            ),
        ),
        404: openapi.Response(description="Not found."),
    },
)
@api_view(['GET'])
def is_following(request: HttpRequest):
    followingid = request.query_params.get('followingid')
    followerid = request.query_params.get('followerid')
    
    follow = get_object_or_404(Follow, following=followingid, follower=followerid)
    serializer = FollowSerializer(follow)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
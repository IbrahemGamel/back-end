from rest_framework import permissions
from rest_framework.authtoken.models import Token

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        token = request.data.get('auth').split(' ')[1].strip()
        print(token)
        token_type = request.data.get('auth').split(' ')[0]
        token_object = Token.objects.get(key=token)
        return False
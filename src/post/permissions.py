from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsPostOwner(BasePermission):
    """
    Custom permission to only allow owners of post instance to edit it.
    """
    message = 'Only owner can perform such action.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.page.owner == request.user

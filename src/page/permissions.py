from rest_framework import permissions
from rest_framework.permissions import BasePermission

from core.constants import Roles


class IsPageOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    message = 'Only owner can perform such action.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class PageIsNotPrivateOrFollower(BasePermission):
    message = 'This page is private.'

    def has_object_permission(self, request, view, obj):
        if request.user in obj.followers.all():
            return True
        return not obj.is_private


class PageIsNotBlocked(BasePermission):
    message = 'This page is blocked.'

    def has_object_permission(self, request, view, obj):
        if request.user.role == Roles.USER.value:
            return not obj.is_blocked
        return True

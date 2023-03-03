from rest_framework.permissions import BasePermission

from core.constants import Roles


class IsModerator(BasePermission):
    """
    Check if the user role is moderator
    """
    message = 'Only Administrator or Moderator can perform such action.'

    def has_permission(self, request, view):
        return request.user.role == Roles.MODERATOR.value

    def has_object_permission(self, request, view, obj):
        return request.user.role == Roles.MODERATOR.value


class IsAdmin(BasePermission):
    """
    Check if the user role is admin
    """
    message = 'Only Administrator can perform such action.'

    def has_permission(self, request, view):
        return request.user.role == Roles.ADMIN.value

    def has_object_permission(self, request, view, obj):
        return request.user.role == Roles.ADMIN.value


class IsAuthAndNotBlocked(BasePermission):
    message = 'Authentication credentials were not provided or user is blocked'

    def has_permission(self, request, view):
        return bool(request.user and
                    request.user.is_authenticated and
                    not request.user.is_blocked)

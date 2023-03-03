from rest_framework.permissions import BasePermission

from core.constants import Roles


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

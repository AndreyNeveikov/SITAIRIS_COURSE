from rest_framework import permissions, exceptions
from rest_framework.permissions import BasePermission


class IsPageOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class PageIsNotPrivateOrFollower(BasePermission):
    message = 'This page is private.'

    def has_object_permission(self, request, view, obj):
        if request.user in obj.followers.all():
            return True
        elif obj.is_private:
            raise exceptions.PermissionDenied(self.message)
        return not obj.is_private

from rest_framework import permissions


class ClientPermission(permissions.BasePermission):
    message = 'Your are a not a end_user'

    def has_permission(self, request, view):
        if not request.user.user_type == 'end_user':
            return True

        return False


class OwnerPermission(permissions.BasePermission):
    message = 'Your are not a Owner'

    def has_permission(self, request, view):
        if request.user.user_type == 'owner':
            return True
        return False

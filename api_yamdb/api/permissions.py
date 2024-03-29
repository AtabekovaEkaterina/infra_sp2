from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdminOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_admin

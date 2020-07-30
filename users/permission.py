from rest_framework.permissions import BasePermission
from .models import User


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, user):
        admin_user = User.objects.get(pk=1)
        return user == request.user or request.user == admin_user

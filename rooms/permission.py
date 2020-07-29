from rest_framework.permissions import BasePermission

# ↓ Custom Permission
# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

# has_permission(self,request,view) : list ,개별 object 에 대한 permission
# has_object_permission(self,request,view,obj) :  detail view 를 위한 permission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, room):
        return room.user == request.user  # True 값 return

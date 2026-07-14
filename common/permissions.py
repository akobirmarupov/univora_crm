from django.core.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "manager")
    

class IsManagernOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'
    
    
def is_admin(user) -> bool:
    return getattr(user, "role", None) == "admin"
 
 
def is_manager(user) -> bool:
    return getattr(user, "role", None) == "manager"
 

def get_visible_queryset(user, queryset):
    if is_admin(user):
        return queryset
    return queryset.filter(user=user)


def check_object_permission(user, obj):
    if is_admin(user):
        return 
    
    if obj.user_id != user.id:
        raise PermissionDenied("Bu ma'lumot sizga tegishli emas.")
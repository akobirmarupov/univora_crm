from django.core.exceptions import PermissionDenied

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
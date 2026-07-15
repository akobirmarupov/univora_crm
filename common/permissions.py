from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "manager")
        )


class IsEmployee(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ("admin", "manager")


class IsManagernOrReadOnly(IsManagerOrReadOnly):

    pass


def is_admin(user) -> bool:
    return getattr(user, "role", None) == "admin"


def is_manager(user) -> bool:
    return getattr(user, "role", None) == "manager"


def is_employee(user) -> bool:
    return getattr(user, "role", None) == "employee"


def get_visible_queryset(user, queryset, owner_field: str = "user"):
    if is_admin(user) or is_manager(user):
        return queryset
    filter_kwargs = {owner_field: user}
    return queryset.filter(**filter_kwargs)


def check_object_permission(user, obj, owner_field: str = "user"):
    if is_admin(user) or is_manager(user):
        return
    owner = getattr(obj, owner_field, None)
    owner_id = getattr(owner, "id", owner)
    if owner_id != user.id:
        raise PermissionDenied("Bu ma'lumot sizga tegishli emas.")
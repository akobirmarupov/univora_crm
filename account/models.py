from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from common.models import BaseModel
from .manager import UserManager


class RoleChoices(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Menejer"


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(blank=True, null=True, unique=True)
    full_name = models.CharField(max_length=60, null=True, blank=True)
    phone_number = models.CharField(max_length=14, unique=True, null=False, blank=False)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MANAGER)
    is_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
 
    def __str__(self):
        return self.full_name or self.phone_number
 
    @property
    def is_admin_role(self) -> bool:
        """common/permissions.py dagi is_admin(user) shu yerga tayanadi."""
        return self.role == RoleChoices.ADMIN
 
    @property
    def is_manager_role(self) -> bool:
        return self.role == RoleChoices.MANAGER
 

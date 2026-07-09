from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin
from django.contrib import admin

from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin, ModelAdmin):
    model = User
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ("id", "phone_number", "full_name", "role", "is_active", "is_staff", "is_confirmed")
    list_filter = ("role", "is_active", "is_staff", "is_confirmed")
    search_fields = ("phone_number", "full_name", "email")
    ordering = ("phone_number",)

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Shaxsiy ma'lumotlar", {"fields": ("full_name", "email")}),
        ("Rol va holat", {
            "fields": ("role", "is_active", "is_staff", "is_confirmed", "is_superuser", "groups", "user_permissions")
        }),
        ("Muhim sanalar", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "full_name", "email", "role", "password1", "password2"),
        }),
    )


admin.site.register(User, CustomUserAdmin)
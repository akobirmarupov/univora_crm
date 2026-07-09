from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("phone_number", "full_name", "email", "role")
        field_classes = {"phone_number": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            del self.fields["username"]
        if "phone_number" in self.fields:
            self.fields["phone_number"].widget.attrs.update({"autofocus": True})


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "phone_number",
            "full_name",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            del self.fields["username"]
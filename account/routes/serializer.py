from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(
            username = attrs.get("phone_number"), 
            password = attrs.get("password"))
        
        if user is None:
            raise serializers.ValidationError("Telefon raqam yoki parol xato.")
        
        if not user.is_active:
            raise serializers.ValidationError("Bu foydalanuvchi faol emas.")
        
        attrs['user'] = user
        return attrs
    

class UserShortSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    role = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
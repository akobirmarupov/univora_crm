from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from common.throttles import LoginThrottle
import re
 
from account.routes.serializer import LoginSerializer, LogoutSerializer, UserShortSerializer
 

_PHONE_RE = re.compile(r"^\+?\d{9,15}$")


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({"access": str(refresh.access_token),"refresh": str(refresh),
                         "user": UserShortSerializer(user).data}, status=status.HTTP_200_OK)
    


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return Response({"detail": "Token yaroqsiz yoki muddati o'tgan."},status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Tizimdan muvaffaqiyatli chiqildi."}, status=status.HTTP_205_RESET_CONTENT)
 

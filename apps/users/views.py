from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    success_messages = {"POST": "Registration successful"}


class LoginView(TokenObtainPairView):
    success_messages = {"POST": "Login successful"}


class RefreshTokenView(TokenRefreshView):
    success_messages = {"POST": "Token refreshed"}

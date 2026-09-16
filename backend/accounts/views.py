from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services import authenticate_user


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate_user(
            email=request.data.get("email"), password=request.data.get("password")
        )
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({"email": user.email})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"email": request.user.email})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

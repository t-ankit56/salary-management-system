from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services import authenticate_user


class LoginView(APIView):
    def post(self, request):
        user = authenticate_user(
            email=request.data.get("email"), password=request.data.get("password")
        )
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({"email": user.email})

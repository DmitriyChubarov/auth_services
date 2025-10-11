from django.shortcuts import render
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, SMSSerializer

from datetime import datetime, timedelta

import jwt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Код отправлен на телефон"}, status=status.HTTP_200_OK)

class SMSView(GenericAPIView):
    serializer_class = SMSSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'phone_number': user.phone_number,
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'iat': datetime.utcnow(),
            'iss': 'auth_service',
            'token_type': 'access'
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY_JWT, algorithm='HS256')

        refresh_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'iss': 'auth_service',
            'token_type': 'refresh'
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY_JWT, algorithm='HS256')

        return Response({
            'detail': 'Успешная авторизация',
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, status=status.HTTP_200_OK)


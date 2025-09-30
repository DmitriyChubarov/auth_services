from django.shortcuts import render
from .serializers import RegisterSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    

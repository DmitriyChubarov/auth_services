from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User
from .services import UserRegistrationService


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2", "phone_number"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {
                "validators": [UniqueValidator(queryset=User.objects.all())]
            },
            "phone_number": {
                "validators": [UniqueValidator(queryset=User.objects.all())]
            },
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError({"detail": "Пароли не совпадают."})

        validate_password(password)
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("password2", None)
        password: str = validated_data.pop("password")
        try:
            user = UserRegistrationService.register_user({"password": password, **validated_data})
            return user
        except IntegrityError:
            raise serializers.ValidationError({"detail": "Пользователь с такими данными уже существует."})
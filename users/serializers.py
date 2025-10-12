from typing import Any, Dict, Optional
import re

from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User
from .services import UserService
from .utils import OTPManager, OTPSendError
from .tasks import send_sms_task


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2", "phone_number"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"validators": [UniqueValidator(queryset=UserService.get_users(), message="Пользователь с таким именем уже существует.")]},
            "phone_number": {"validators": [UniqueValidator(queryset=UserService.get_users(), message="Пользователь с таким номером уже существует.")]},
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        password: str = attrs.get("password")
        password2: str = attrs.get("password2")
        username: str = attrs.get("username")
        phone_number: str = attrs.get("phone_number")
        if password != password2:
            raise serializers.ValidationError({"detail": "Пароли не совпадают."})

        if not re.match(r'^8\d{10}$', phone_number):
            raise serializers.ValidationError({"detail": "Введен некорректный номер телефона. Формат: 8XXXXXXXXXX"})
        validate_password(password)
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("password2", None)
        password: str = validated_data.pop("password")
        try:
            user: User = UserService.register_user({"password": password, **validated_data})
            return user
        except Exception as e:
            raise serializers.ValidationError({'detail': str(e)})


class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        username_or_phone : str = attrs.get("username_or_phone")
        password: str = attrs.get("password")
        try:
            user: Optional[User] = UserService.get_user_by_phone_or_name(username_or_phone)
        except Exception:
            raise serializers.ValidationError({"detail": "Ошибка при поиске пользователя."})

        if not user:
            raise serializers.ValidationError({"detail": "Пользователь не существует, пройдите регистрацию."})

        if not check_password(password, user.password):
            raise serializers.ValidationError({"detail": "Введён неправильный пароль."})
        
        otp_manager = OTPManager()
        try:
            otp_code: str = otp_manager.create_otp()
            otp_manager.save_otp(username_or_phone, otp_code)
        except OTPSendError as e:
            raise serializers.ValidationError({"detail": str(e)})
        except Exception:
            raise serializers.ValidationError({"detail": "Не удалось подготовить код подтверждения."})
            
        if user and getattr(user, "phone_number", None):
            send_sms_task.delay(user.phone_number, otp_code)

        return attrs

class SMSSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField()
    sms_code = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        username_or_phone: str = attrs.get("username_or_phone")
        sms_code: str = attrs.get("sms_code")

        otp_manager = OTPManager()
        try:
            otp_code = otp_manager.get_otp(username_or_phone)
        except OTPSendError as e:
            raise serializers.ValidationError({'detail': str(e)})
        
        if otp_code != sms_code:
            raise serializers.ValidationError({'detail': 'Введён неверный код.'})

        user: Optional[User] = UserService.get_user_by_phone_or_name(username_or_phone)
        if not user:
            raise serializers.ValidationError({'detail': 'Не удалось найти данные пользователя. Попробуйте войти заново.'})

        otp_manager.delete_otp(username_or_phone)

        attrs['user'] = user
        return attrs     


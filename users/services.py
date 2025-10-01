from typing import Any, Dict

from django.db import IntegrityError, transaction

from .models import User


class UserRegistrationService:
    @staticmethod
    def register_user(validated_data: Dict[str, Any]) -> User:
        try:
            with transaction.atomic():
                user = User.objects.create_user(**validated_data)
                return user
        except IntegrityError as exc:
            raise exc
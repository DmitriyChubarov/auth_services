from typing import Any, Dict, Optional

from django.db import IntegrityError, transaction

from django.db.models import Q

from .models import User


class UserService:
    @staticmethod
    def register_user(validated_data: Dict[str, Any]) -> User:
        try:
            with transaction.atomic():
                user = User.objects.create_user(**validated_data)
                return user
        except IntegrityError as exc:
            raise exc

    @staticmethod
    def get_users() -> User:
        try:
            with transaction.atomic():
                user = User.objects.all()
                return user
        except Exception as exc:
            raise exc

    @staticmethod
    def get_user_by_phone_or_name(username_or_phone: str) -> Optional[User]:
        try:
            with transaction.atomic():
                user = User.objects.filter(Q(username=username_or_phone) | Q(phone_number=username_or_phone)).first()
                return user
        except IntegrityError as exc:
            raise exc
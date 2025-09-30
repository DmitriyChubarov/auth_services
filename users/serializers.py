from rest_framework import serializers
from .models import User

from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'phone_number']

    def create(self, validated_data) -> User:
        validated_data.pop('password2')
        user = User(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
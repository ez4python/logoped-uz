from rest_framework import serializers

from apps.users.validators import validate_phone_number


class UserAuthCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])
    
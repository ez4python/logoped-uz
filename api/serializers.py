from rest_framework import serializers

from apps.users.validators import validate_phone_number


class UserAuthCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])


class VerifyAuthCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])
    code = serializers.CharField(max_length=6)

    def validate_code(self, value):
        """
        bu yerda kod uzunligi va faqat raqamlardan tashkil topganligi tekshiriladi
        """

        # checking length
        if len(value) != 6:
            raise serializers.ValidationError('The code must be exactly 6 digits long.')

        # checking code -> only digits
        if not value.is_digit():
            raise serializers.ValidationError('The code must contain only digits.')

        return value


class RegisterUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

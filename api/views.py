from random import randint

from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import UserAuthCodeSerializer, VerifyAuthCodeSerializer, RegisterUserSerializer
from apps.users.models import User


@extend_schema(
    tags=['Auth'],
    methods=['POST'],
    request=UserAuthCodeSerializer,
    description='User enters phone number and receives a 6-digit numeric code in response.',
    responses={200: dict, 400: dict}
)
class UserAuthCodeAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            six_digits_pass = str(randint(100000, 999999))
            cache.set(
                key=phone_number,
                value=six_digits_pass,
                timeout=60,
            )
            return Response(
                {
                    'message': 'Verification code sent successfully.',
                    'code': six_digits_pass
                }, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Auth'],
    methods=['POST'],
    request=VerifyAuthCodeSerializer,
    description='Verify the user phone number and authentication code, returning access and refresh tokens.',
    responses={200: dict, 202: dict, 400: dict}
)
class UserAuthCodeVerifyAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = VerifyAuthCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        cached_code = cache.get(phone_number)

        if not cached_code:
            return Response(
                {'detail': 'Verification code expired or not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_code != code:
            return Response(
                {'detail': 'Invalid varification code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache.delete(phone_number)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {
                    'detail': 'User not found. Please complete registration.',
                    'needs_registration': True
                },
                status=status.HTTP_202_ACCEPTED
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['Auth'],
    methods=['POST'],
    request=RegisterUserSerializer,
    description='User ism, familiya va telefon raqami orqali ro\'yxatdan o\'tadi.',
    responses={201: dict, 400: dict}
)
class RegisterUserAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']

        user = User.objects.create(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED
        )

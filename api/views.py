from random import randint

from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserAuthCodeSerializer


@extend_schema(
    tags=['Auth'],
    methods=['POST'],
    request=UserAuthCodeSerializer,
    description='User telefon raqamini kiritib, responseda 6-xonali, raqamli kod oladi.',
    responses={200: dict, 400: dict, 500: dict}
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
            return Response({'code': six_digits_pass}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

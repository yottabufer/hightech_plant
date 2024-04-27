from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ..serializers.user import (
    UserRegistrationSerializer,
    AuthTokenSerializer,
    UserProfileSerializer
)

User = get_user_model()


class UserRegistrationAPI(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def send_activation_email(self, user):
        link = 'https://localhost:8000/activate/{user_uuid}/{token}'.format(
            user_uuid=user.uuid,
            token=user.auth_token.key)

        send_mail(
            'Подтверждение регистрации',
            f'Привет, {user.email}! Для активации вашего аккаунта пройдите по ссылке: {link}',
            'yottabufer@yandex.ru',
            [user.email],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Был бы свой SMTP сервер, использовалась бы метод send_activation_email вместе с django.send_mail
        # self.send_activation_email(serializer.instance)
        link = f'http://localhost:8000/activate/?uuid={serializer.instance.uuid}'
        return Response(
            {'Пользователь успешно зарегистрирован': f'Для активации вашего аккаунта пройдите по ссылке: {link}'},
            status=status.HTTP_201_CREATED,
            headers=headers)


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_uuid': user.uuid,
            'email': user.email
        })


class UserProfileRetrieve(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ActivateUser(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        uuid = request.query_params.get('uuid')
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_active:
            return Response({'message': 'User is already active.'}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save()

        return Response({'message': 'User activated successfully.'}, status=status.HTTP_200_OK)
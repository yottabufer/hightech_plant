from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    ListAPIView,
    get_object_or_404
)
from ..serializers.user import (
    UserRegistrationSerializer,
    AuthTokenSerializer,
    UserSerializer,
    UserPasswordUpdateSerializer,
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
    EmailUpdateSerializer
)

User = get_user_model()


class UserRegistration(CreateAPIView):
    """
    Регистрация пользователя и получение ссылки для активации
    """
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def send_activation_email(self, user):
        link = f'http://localhost:8000/api/activate/?uuid={user.uuid}'

        send_mail(
            'Подтверждение регистрации',
            f'Привет, {user.email}! Для активации вашего аккаунта пройдите по ссылке: {link}',
            'yottabufer@gmail.com',
            [user.email],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Был бы свой SMTP сервер, использовался бы метод send_activation_email вместе с django.send_mail
        # self.send_activation_email(serializer.instance)
        link = f'http://localhost:8000/api/activate/?uuid={serializer.instance.uuid}'
        return Response(
            {'Пользователь успешно зарегистрирован': f'Для активации вашего аккаунта пройдите по ссылке: {link}'},
            status=status.HTTP_201_CREATED,
            headers=headers)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Классическая авторизация пользователя с помощью токена
    """
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
    """
    Получение информации о своём аккаунте
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ActivateUser(RetrieveAPIView):
    """
    Активация пользователя по ссылке, которая получена при регистрации
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        uuid = request.query_params.get('uuid')
        user = get_object_or_404(User, uuid=uuid)
        if user.is_active:
            return Response({'message': 'Пользователь уже активирован'}, status=status.HTTP_200_OK)

        user.is_active = True
        user.is_email_verified = True
        user.save()

        return Response({'message': 'Пользователь активирован'}, status=status.HTTP_200_OK)


class UserList(ListAPIView):
    """
    Получение списка всех пользователей
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class ResetPasswordRetrieve(UpdateAPIView):
    """
    Запрос на сброс пароля
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        email = self.request.data.get('email')
        user = get_object_or_404(User, email=email)
        # Был бы свой SMTP сервер, использовался бы метод django.send_mail
        link = f'http://localhost:8000/api/new-password/?uuid={user.uuid}'
        return Response(
            {'Вам отправлена ссылка для сброса пароля': f'Для сброса пароля пройдите по ссылке: {link}'},
            status=status.HTTP_200_OK, )


class NewPasswordUpdate(UpdateAPIView):
    """
    Непосредственно сброс пароля после запроса в ResetPasswordRetrieve
    """
    serializer_class = UserPasswordUpdateSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def update(self, request, *args, **kwargs):
        uuid = request.query_params.get('uuid')
        if not uuid:
            return Response({'Error': 'uuid обязателен к заполнению'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, uuid=uuid)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Message': 'Сброс пароля выполнен'},
                        status=status.HTTP_200_OK)


class ChangePasswordUpdate(UpdateAPIView):
    """
    Смена пароля при авторизованном пользователе
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            if not self.object.check_password(old_password):
                return Response({'Message': 'Неверный старый пароль'}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.validated_data['new_password'])
            self.object.save()
            return Response({'Message': 'Пароль успешно изменён'}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdate(UpdateAPIView):
    """
    Обновление данных профиля пользователя
    """
    queryset = User.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'uuid'

    def get_object(self):
        return self.request.user


class EmailUpdate(UpdateAPIView):
    """
    Обновление email пользователя
    """
    serializer_class = EmailUpdateSerializer
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()
    lookup_field = 'uuid'

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if self.object.email == serializer.validated_data['new_email']:
                return Response({'Message': 'Новый email совпадает со старым'},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.email = serializer.validated_data['new_email']
            self.object.is_email_verified = False
            self.object.save()
            user = self.get_object()
            link = f'http://localhost:8000/api/verified-email/'
            return Response({'Message': 'email успешно изменён',
                             'Для подтверждения нового email перейдите по ссылке': f'{link}',
                             'Body->form-data->uuid': f'{user.uuid}',
                             'Body->form-data->email': f'{user.email}', },
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifiedEmail(UpdateAPIView):
    """
    Подтверждение электронной почты пользователя
    """
    serializer_class = EmailUpdateSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def put(self, request, *args, **kwargs):
        uuid = request.data.get('uuid')
        email = request.data.get('email')
        if not uuid or not email:
            return Response({'Error': 'uuid и email обязательны к заполнению'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_object_or_404(User, uuid=uuid, email=email)
            user.is_email_verified = True
            user.save()
            return Response({'Message': 'Email успешно подтвержден'},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'Message': 'Email не найден'},
                            status=status.HTTP_404_NOT_FOUND)

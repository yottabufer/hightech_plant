from uuid import uuid4
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Модель для Пользователя
    """
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True, db_index=True)
    email = models.EmailField(unique=True, verbose_name='email', db_index=True)
    first_name = models.CharField(max_length=30, default='', verbose_name='Имя')
    last_name = models.CharField(max_length=30, default='', verbose_name='Фамилия')

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    time_updated = models.DateTimeField(auto_now=True, verbose_name='время изменения')

    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Администратор')
    is_email_verified = models.BooleanField(default=False, verbose_name='Подтвержден email')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.email} -- {self.uuid}'

    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff

    class Meta:
        default_permissions = ()
        permissions = (
            ('create_any_user', 'Создание любого пользователя'),
            ('view_any_user', 'Просмотр информации любого пользователя'),
            ('change_any_user', 'Изменение любого пользователя'),
            ('delete_any_user', 'Удаление любого пользователя'),
        )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

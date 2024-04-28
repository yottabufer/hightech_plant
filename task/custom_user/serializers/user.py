from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'first_name', 'last_name',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Сериализатор для авторизации пользователя
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if not user:
            raise serializers.ValidationError(
                detail='Не удается авторизоваться с предоставленными учетных данных',
                code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Стандартный сериализатор для пользователя
    """

    class Meta:
        model = User
        fields = ('uuid', 'email', 'first_name', 'last_name', 'date_joined',
                  'time_updated', 'is_active', 'is_email_verified')


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для сбоса пароля пользователя
    """
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False)

    class Meta:
        model = User
        fields = ('email', 'new_password')

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return attrs

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['new_password'])
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля пользователя
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False)
    new_password = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный старый пароль')
        return value

    def validate(self, attrs):
        if attrs['new_password'] == attrs['old_password']:
            raise serializers.ValidationError('Новый пароль не может совпадать со старым')
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля пользователя
    """

    def validate(self, attrs):
        print(self.context['request'].user.first_name)
        print(self.context['request'].user.last_name)
        if (attrs['first_name'] == self.context['request'].user.first_name or
                attrs['last_name'] == self.context['request'].user.last_name):
            raise serializers.ValidationError('Новое и старое имя не должны совпадать', code='conflict')
        return attrs

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        read_only_fields = ['email']


class EmailUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления email пользователя
    """
    new_email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['new_email']

"""
Сериализаторы для юзер API.
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для объекта юзера."""

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Создает и возвращает юзера."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Обновление и возвращение юзера."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """Валидация данных юзера."""
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )
        if not user:
            message = _('Не удается войти с введенными данными.')
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs

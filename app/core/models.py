"""
Модели Базы Данных.
"""

import os
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


def recipe_image_file_path(instanse, filename):
    """Генерация пути для изображения рецепта."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Менеджер для работы с юзерами."""

    def create_user(self, username, password=None, **extra_fields):
        """Команда создания юзера."""
        if not username:
            raise ValueError('Username обязателен к заполнению.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        """Команда создания админа."""
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Модель кастомного юзера."""

    username = models.CharField(
        max_length=255, unique=True, verbose_name='юзернейм'
    )
    name = models.CharField(max_length=255, verbose_name='имя')
    is_active = models.BooleanField(default=True, verbose_name='активен')
    is_staff = models.BooleanField(default=False, verbose_name='персонал')
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Recipe(models.Model):
    """Объект рецепта."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки'
    )
    link = models.CharField(max_length=255, blank=True, verbose_name='Ссылка')
    tags = models.ManyToManyField('Tag', verbose_name='Тег')
    ingredients = models.ManyToManyField(
        'Ingredient', verbose_name='Ингредиент'
    )
    image = models.ImageField(
        null=True, upload_to=recipe_image_file_path, verbose_name='Изображение'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Тег для фильтрации рецептов."""

    name = models.CharField(max_length=255, verbose_name='Тег')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент для рецептов."""

    name = models.CharField(max_length=255, verbose_name='Ингредиент')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.Case,
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name

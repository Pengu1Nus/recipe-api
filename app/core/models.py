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

    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    objects = UserManager()


class Recipe(models.Model):
    """Объект рецепта."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cooking_time = models.PositiveSmallIntegerField()
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Тег для фильтрации рецептов."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент для рецептов."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.Case,
    )

    def __str__(self):
        return self.name

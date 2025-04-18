"""
Тест моделей.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


class ModelTests(TestCase):
    """Класс для теста моделей."""

    def test_create_user_with_username_successful(self):
        """Тест создания юзера с валидными данными."""
        username = 'testuser'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
        )
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_without_username_raises_error(self):
        """
        Тест случая, при попытке создания юзера без username
        пробрасывает ошибку.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """Тест создания админа."""
        user = get_user_model().objects.create_superuser(
            'superuser',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Тест создания рецепта."""
        user = get_user_model().objects.create_user(
            'testUser',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Название рецепта',
            cooking_time=5,
            description='Подробное описание рецепта.',
        )

        self.assertEqual(str(recipe), recipe.title)

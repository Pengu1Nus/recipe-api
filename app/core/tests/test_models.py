"""
Тест моделей.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def create_user(username='testUser', password='testpass123'):
    """Вспомогательная функция для создания пользователя."""
    return get_user_model().objects.create_user(username, password)


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

    def test_create_tag(self):
        """Тест создания тега."""

        tag = models.Tag.objects.create(name='Тег')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Тест создания ингредиента."""

        ingredient = models.Ingredient.objects.create(
            name='Первый ингредиент',
        )
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Тест генерации пути для изображений."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example-img.jpg')
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')

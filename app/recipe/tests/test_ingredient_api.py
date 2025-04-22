"""
Тест для API ингредиентов.
"""

from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """
    Вспомогательная функция, возвращает url конкретного ингредиента по id.
    """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(username='testUser', password='testpass1223'):
    """Вспомогательная функция — создает и возвращает юзера."""
    return get_user_model().objects.create_user(
        username=username, password=password
    )


class PublicIngredientApiTests(TestCase):
    """Тест неаутентифицированных запросов."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Тест неаутентифицированный пользователь не может получить ингредиент.
        """
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Тест ингредиента для аутентифицированных пользователей."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Тест получения списка ингредиентов."""
        Ingredient.objects.create(user=self.user, name='Тестовый ингредиент 1')
        Ingredient.objects.create(user=self.user, name='Тестовый ингредиент 2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
        Тест получения списка ингредиентов доступна только
        аутентифицированному пользователю.
        """
        user2 = create_user(username='TestUser')
        Ingredient.objects.create(user=user2, name='Соль')
        ingredient = Ingredient.objects.create(user=self.user, name='Перец')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Тест обновления ингредиента."""
        ingredient = Ingredient.objects.create(user=self.user, name='Сахар')
        payload = {'name': 'Корица'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Тест удаления ингредиента."""
        ingredient = Ingredient.objects.create(user=self.user, name='Мука')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Тест списка ингредиентов, указанных в рецептах."""
        ing1 = Ingredient.objects.create(user=self.user, name='Морковь')
        ing2 = Ingredient.objects.create(user=self.user, name='Лук')
        recipe = Recipe.objects.create(
            title='Плов',
            cooking_time=55,
            user=self.user,
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Тест — отфильтрованные ингредиенты возвращает уникальный список."""
        ing = Ingredient.objects.create(user=self.user, name='Картофель')
        Ingredient.objects.create(user=self.user, name='Грибы')
        recipe1 = Recipe.objects.create(
            title='Жареная Картошка',
            cooking_time=60,
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Тальятелле',
            cooking_time=20,
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

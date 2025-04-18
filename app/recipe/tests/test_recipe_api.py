"""
Тест API рецепта.
"""

from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Вспомогательная функция, возвращает url конкретного рецепта по id."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Вспомогательная функция для создания рецепта."""
    defaults = {
        'title': 'Название рецепта',
        'cooking_time': 55,
        'description': 'Описание рецепта',
        'link': 'http://example.com',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Вспомогательная функция — создает и возвращает юзера."""
    return get_user_model().objects.create_user(params)


class PublicRecipApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username='testUser1', password='testpass123')
        self.recipe = Recipe.objects.create(
            title='Тестовый рецепт',
            cooking_time=30,
            description='Описание тестового рецепта',
            user=self.user,
        )

    def test_unauthorized_user_cannot_create_recipe(self):
        """
        Тест случаев, когда неавторизованный юзер не может создать рецепт.
        """
        payload = {
            'title': 'Название рецепта',
            'cooking_time': 30,
            'description': 'Описание рецепта',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_recipe(self):
        """
        Тест случаев, когда неавторизованный юзер не может удалить рецепт.
        """
        url = detail_url(self.recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())


class PrivateRecipeApiTests(TestCase):
    """Тест рецепта для аутентифицированных пользователей."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username='testUser1', password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Тест получения списка рецептов."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Тест — получение рецепта по id."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Тест создания рецепта."""
        payload = {
            'title': 'Название рецепта',
            'cooking_time': 30,
            'description': 'Описание рецепта',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Тест частичного обновления рецепта."""
        original_link = 'https://example.com/recipe.html'
        recipe = create_recipe(
            user=self.user,
            title='Название рецепта',
            link=original_link,
        )
        payload = {'title': 'Новое название рецепта'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Тест полного обновления рецепта."""
        recipe = create_recipe(
            user=self.user,
            title='Название рецепта',
            link='https://example.com/recipe.html',
            description='Описание рецепта.',
        )

        payload = {
            'title': 'Новое название рецепта',
            'link': 'https://example.com/new-ecipe.html',
            'description': 'Новое описание рецепта',
            'cooking_time': 90,
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Тест — попытка изменения автора рецепта, возвращает ошибку."""
        new_user = create_user(username='testUser2', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Тест удаления рецепта."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Тест попытка удаления рецепта другого автора возвращает ошибку."""
        new_user = create_user(username='testAnotherUser2', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

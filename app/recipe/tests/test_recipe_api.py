"""
Тест API рецепта.
"""

import os
import tempfile

from core.models import Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Вспомогательная функция, возвращает url конкретного рецепта по id."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Вспомогательная функция для создания URL загрузки изображения."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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


def create_user(username='testUser', password='testpass1223'):
    """Вспомогательная функция — создает и возвращает юзера."""
    return get_user_model().objects.create_user(
        username=username, password=password
    )


class PublicRecipApiTests(TestCase):
    """Тест неаутентифицированных запросов."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username='testUser1', password='testpass123')
        self.recipe = Recipe.objects.create(
            title='Тестовый рецепт',
            cooking_time=30,
            description='Описание тестового рецепта',
            user=self.user,
        )
        self.tag_breakfast = Tag.objects.create(user=self.user, name='Завтрак')
        self.tag_dinner = Tag.objects.create(user=self.user, name='Ужин')

        self.ingredient_egg = Ingredient.objects.create(
            user=self.user, name='Яйцо'
        )
        self.ingredient_cheese = Ingredient.objects.create(
            user=self.user, name='Сыр'
        )

        self.recipe1 = create_recipe(user=self.user, title='Омлет')
        self.recipe1.tags.add(self.tag_breakfast)
        self.recipe1.ingredients.add(self.ingredient_egg)

        self.recipe2 = create_recipe(user=self.user, title='Паста')
        self.recipe2.tags.add(self.tag_dinner)
        self.recipe2.ingredients.add(self.ingredient_cheese)

    def test_filter_recipes_by_tags(self):
        """Тест фильтрации рецептов по тегу."""
        response = self.client.get(RECIPES_URL, {'tags': 'Завтрак'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.recipe1.title)

    def test_filter_recipes_by_ingredients(self):
        """Тест фильтрации рецептов по ингредиенту."""
        response = self.client.get(RECIPES_URL, {'ingredients': 'Яйцо'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.recipe1.title)

    def test_filter_recipes_multiple_parameters(self):
        """Тест фильтрации рецептов по нескольким параметрам."""
        response = self.client.get(
            RECIPES_URL,
            {
                'tags': 'Ужин',
                'ingredients': 'Сыр',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.recipe2.title)

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
        recipe = Recipe.objects.get(title=payload['title'])

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

    def test_create_recipe_with_new_tags(self):
        """Тест создания нового рецепта с новыми тегами."""
        payload = {
            'title': 'Название рецета',
            'cooking_time': 30,
            'tags': [{'name': 'Завтрак'}, {'name': 'Обед'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_exising_tags(self):
        """Тест создания рецепта с уже существующим тегом."""

        existing_tag = Tag.objects.create(user=self.user, name='Завтрак')
        payload = {
            'title': 'Название рецета',
            'cooking_time': 30,
            'tags': [{'name': 'Завтрак'}, {'name': 'Ужин'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(existing_tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Тест создания тега при обновлении рецепта."""
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Обед'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Обед')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Тест присвоения существующего тега при обновлении рецепта."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Завтрак')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Обед')
        payload = {'tags': [{'name': 'Обед'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Тест удаления тегов рецепта."""
        tag = Tag.objects.create(user=self.user, name='Десерт')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredient(self):
        """Тест создания рецепта с новым ингредиентом."""
        payload = {
            'title': 'Новый рецепт',
            'cooking_time': 30,
            'ingredients': [{'name': 'Мука'}, {'name': 'Сахар'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_exising_ingredient(self):
        """Тест создания рецепта с уже существующим ингредиентом."""

        existing_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Сахар',
        )
        payload = {
            'title': 'Название рецета',
            'cooking_time': 30,
            'ingredients': [{'name': 'Сахар'}, {'name': 'Соль'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(existing_ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Тест создания ингредиента при обновлении рецепта."""
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'Сахар'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Сахар')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Тест присвоения существующего ингредиента при обновлении рецепта."""
        ingredient_salt = Ingredient.objects.create(
            user=self.user,
            name='Соль',
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_salt)

        ingredient_sugar = Ingredient.objects.create(
            user=self.user,
            name='Сахар',
        )
        payload = {'ingredients': [{'name': 'Сахар'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_sugar, recipe.ingredients.all())
        self.assertNotIn(ingredient_salt, recipe.ingredients.all())

    def test_clear_recipe_ingredient(self):
        """Тест удаления ингредиентов рецепта."""
        ingredient = Ingredient.objects.create(user=self.user, name='Сыр')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTests(TestCase):
    """Тесты для URL загрузки изображений."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testUser',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Тест загрузки изображения в рецепт."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Тест загрузки некорректного изображения."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notvalidimg'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

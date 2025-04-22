"""
Тест API тегов.
"""

from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Вспомогательная функция для создания url тега."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(username='testUser', password='testpass1223'):
    """Вспомогательная функция — создает и возвращает юзера."""
    return get_user_model().objects.create_user(
        username=username, password=password
    )


class PublicTagsApiTests(TestCase):
    """Тест неаутентифицированных запросов."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Тест, требование авторизации для получения списка тегов."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Тест аутентифицированных запросов."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Тест получения списка тегов."""
        Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serilizer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def test_tags_limit_to_user(self):
        user2 = create_user(username='AnotherUser', password='testpass123')
        Tag.objects.create(user=user2, name='Lunch')
        tag = Tag.objects.create(user=self.user, name='Brunch')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Тест обновления тега."""
        tag = Tag.objects.create(user=self.user, name='New Tag')

        payload = {'name': 'Another new Tag'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Тест удаления тега."""
        tag = Tag.objects.create(user=self.user, name='New Tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Тест списка тегов, указанных по рецептам."""

        tag1 = Tag.objects.create(user=self.user, name='Завтрак')
        tag2 = Tag.objects.create(user=self.user, name='Обед')
        recipe = Recipe.objects.create(
            title='Тосты',
            cooking_time=10,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Тест — отфильтрованные теги возвращает уникальный список."""
        tag = Tag.objects.create(user=self.user, name='Завтрак')
        Tag.objects.create(user=self.user, name='Ужин')
        recipe1 = Recipe.objects.create(
            title='Блины',
            cooking_time=5,
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Пицца',
            cooking_time=30,
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

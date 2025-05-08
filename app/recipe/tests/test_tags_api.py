"""
Тест API тегов.
"""

from core.models import Tag
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
        Tag.objects.create(name='Breakfast')
        Tag.objects.create(name='Dinner')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serilizer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def test_update_tag(self):
        """Тест обновления тега."""
        tag = Tag.objects.create(name='New Tag')

        payload = {'name': 'Another new Tag'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Тест удаления тега."""
        tag = Tag.objects.create(name='Tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(name='Tag')
        self.assertFalse(tags.exists())

"""
Тест API юзера.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Создает и возвращает тестового юзера."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Тесты API для неаутентифицированных пользователей."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Тест проверки создания юзера с валидными данными."""
        payload = {
            'username': 'testUsername',
            'password': 'testpass123',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(username=payload['username'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_username_exists_error(self):
        """
        Тест при попытке создания юзера с существующим username,
        пробросасывается ошибка.
        """
        payload = {
            'username': 'testUsername',
            'password': 'testpass123',
            'name': 'Test User',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """
        Тест, при попытке создания юзера с небезопасным паролем,
        пробрасывается ошибка.
        """
        payload = {
            'username': 'testUsername',
            'password': 'te',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model()
            .objects.filter(username=payload['username'])
            .exists()
        )
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Тест корректного создания токена для валидных данных юзера."""
        user_details = {
            'name': 'Test User',
            'username': 'testUsername',
            'password': 'testpass123',
        }
        create_user(**user_details)
        payload = {
            'username': user_details['username'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_incorrect_password(self):
        """Тест случая попытки получения токена с некорректным паролем."""
        user_details = {
            'name': 'Test User',
            'username': 'testUsername',
            'password': 'goodpassword123',
        }
        create_user(**user_details)
        payload = {
            'username': user_details['username'],
            'password': 'differentpassword123',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Тест случая попытки получения токена с некорректным паролем."""
        payload = {
            'username': 'testUsername',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Тест для проверки недоступности эндпоинта
        для неаутентифицированных юзеров.
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Тест API для аутентифицированных юзеров."""

    def setUp(self):
        self.user = create_user(
            username='testUsername',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Тест корректного получения профиля юзера."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                'username': self.user.username,
                'name': self.user.name,
            },
        )

    def test_post_me_not_allowed(self):
        """Тест для проверки, что POST метод недоступен для эндпоинта."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Тест для проверки обновления данных юзера."""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

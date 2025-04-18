"""
Тест админ панели.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTest(TestCase):
    """Тесты для админки Django."""

    def setUp(self):
        """Создание юзера и клиента."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin_username',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            username='user_testuser',
            password='testpassword123!',
            name='Test User',
        )

    def test_user_list(self):
        """Тест, что юзеры отображаются на странице."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.username)

    def test_edit_user_page(self):
        """Тест редактирования страницы юзера."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Тест создания страницы юзера."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

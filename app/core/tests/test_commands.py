from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2Error


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_check):
        """Тест команды, которая проверяет случай, когда БД доступна."""

        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Тест команды, которая проверяет случай, когда БД недоступна."""
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 2 + [True]
        )
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 5)
        patched_check.assert_called_with(databases=['default'])

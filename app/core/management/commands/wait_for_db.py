"""
Django команда для ожидания доступности БД.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Команда для ожидания БД."""

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\nОжидание Базы Данных...\n'))
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(
                    self.style.ERROR(
                        'База Данных недоступна, ожидание 1 сек...'
                    )
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('База Данных доступна'))

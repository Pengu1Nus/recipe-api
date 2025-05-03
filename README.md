# Recipe API 🍽️

Recipe API — это сервис, предназначенный для управления рецептами, ингредиентами. Поддерживает CRUD операции и функции аутентификации.

## Документация API
Полная документация API доступна через Swagger:

🔗 **[Swagger Docs](https://recipe-api.sytes.net/api/docs/)**

## 🚀 Особенности
- CRUD операции для рецептов
- Аутентификация и авторизация
- Отслеживание ингредиентов
- Фильтрация по тегам рецептов

## 🛠️ Стек
- Django ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
- Django Rest Framework ![DRF](https://img.shields.io/badge/DRF-red?style=flat&logo=django&logoColor=white)
- PostgreSQL ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
- Nginx ![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)
- Docker ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)


## 🏁 Локальный запуск

1. Клонировать репозиторий:

```Shell
git clone https://github.com/Pengu1Nus/recipe-api.git
cd recipe-api
```

2. Запуск контейнера разработки

```Shell
docker compose up
```

3. Выполнение команд в контейнере
```Shell
# Проверка кода на соотвествие PEP
docker compose run --rm backend sh -c 'flake8'
```
```Shell
# Запуск тестов
docker compose run --rm backend sh -c 'python manage.py test'
```

## 🔥 Основные Эндпоинты Рецептов
| Метод | Эндпоинт | Описание |
| ------ | -------- | ----------- | 
| GET | /api/recipe/recipes/	| Получение списка рецептов |
| GET | /api/recipe/recipes/{id}/ |	Получение рецепта по ID |
| POST | /api/recipe/recipes/ |	Создание нового рецепта |
| PUT | /api/recipe/recipes/{id}/ |	Обновление рецепта |
| DELETE | /api/recipe/recipes/{id}/ |	Удаление рецепта |

##  💁🏻‍♂️ API Основные Эндпоинты для управления пользователем
| Метод | Эндпоинт | Описание |
| ------ | -------- | ----------- | 
| POST | /api/user/create |	Регистрация нового пользователя |
| POST | /api/user/token |	Получение токена |


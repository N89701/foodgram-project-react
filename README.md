# Продуктовый помощник Foodgram

## Описание  
Проект является кулинарным блогом-соцсетью, в которой пользователи могут выкладывать свои рецепты, просматривать рецепты других пользователей и подписываться на них, а также добавлять рецепты в избранное и список покупок.

## Стек технологий
Django, Django Rest Framework, React, Docker, PostgreSQL

## Локальный запуск проекта  
Для локального запуска необходимо:  
Клонировать репозиторий:  
```
git clone git@github.com:N89701/foodgram-project-react
```
Перейдите в папку infra:
```
cd infra
```
Запустите команду:
```
docker-compose up
```
Внутри контейнера выполните команды сборки статики и применения миграций:
```
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py migrate
```
Зарегистрируйте админа
```
docker-compose exec backend python manage.py createsuperuser
```
Зайдите в админку localhost/admin/ и создайте пару тегов

## Авторы проекта
- Николай Хван, https://github.com/N89701 - бэкенд
- Яндекс.Практикум - фронтенд
- Андрей Дубинчик - ревьюер

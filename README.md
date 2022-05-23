# Учебный проект "Foodgram"

##  Приложение «Продуктовый помощник».

Сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов, создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Реализовал backend и API для взаимодействия с ним, настроил контейнеризацию готового проекта в Docker-контейнерах. В проекте был готовый фронтенд, одностраничное приложение на фреймворке React, которое взаимодействует с API через удобный пользовательский интерфейс. 

Проект реализован на Django REST Framework.

## Как локально запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Saladin366/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

или

```
source venv/bin/activate
```

Создать и заполнить файл .env с переменными окружения для settings.py:

```
cd infra
```

```
touch .env
```

Создать и запустить контейнеры с проектом:

```
docker-compose up -d --build
```

Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Добавить данные в базу:

```
docker-compose exec backend python add_data.py
```

Перейти по ссылке:

http://localhost/

Документация к API:

http://localhost/api/docs/

Админ панель:

http://localhost/admin/

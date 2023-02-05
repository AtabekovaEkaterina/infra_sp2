# Проект YaMDb
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Title). Произведения делятся на категории: "Книги", "Фильмы", "Музыка". Список категорий (Category) может быть расширен.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории "Книги" могут быть произведения "Винни Пух и все-все-все" и "Марсианские хроники", а в категории "Музыка" — песня "Давеча" группы "Насекомые" и вторая сюита Баха. Произведению может быть присвоен жанр из списка предустановленных (например, "Сказка", "Рок" или "Артхаус"). Новые жанры может создавать только администратор.
Благодарные или возмущённые читатели оставляют к произведениям текстовые отзывы (Review) и выставляют произведению рейтинг.

# Ресурсы API YaMDb
**AUTH**: аутентификация.

**USERS**: пользователи.

**TITLES**: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).

**CATEGORIES**: категории (типы) произведений ("Фильмы", "Книги", "Музыка").

**GENRES**: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.

**REVIEWS**: отзывы на произведения. Отзыв привязан к определённому произведению.

**COMMENTS**: комментарии к отзывам. Комментарий привязан к определённому отзыву.

# Алгоритм регистрации пользователей
Пользователь отправляет POST-запрос с параметром email и username на `/api/v1/auth/`.
YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email (письмо будет находиться в папке sent_emails, которая лежит в корне).
Пользователь отправляет POST-запрос с параметрами email и confirmation_code на `/api/v1/auth/token/`, в ответе на запрос ему приходит token (JWT-токен).
Эти операции выполняются один раз, при регистрации пользователя. В результате пользователь получает токен и может работать с API, отправляя этот токен с каждым запросом.

# Пользовательские роли и права доступа
**Аноним** — может просматривать описания произведений, читать отзывы и комментарии.

**Аутентифицированный пользователь (user)** — может читать всё, как и Аноним, дополнительно может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произвдений. Эта роль присваивается по умолчанию каждому новому пользователю.

**Модератор (moderator)** — те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.

**Администратор (admin)** — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.

**Суперюзер Django** — должен всегда обладать правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.

# Технологии
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) Python 3.7<br/>
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green) Django 2.2.16

# Инструкция по запуску
1. Склонируйте репозиторий 
```git@github.com:AtabekovaEkaterina/infra_sp2.git
```
2. В дирктории проекта infa/ создайте файл .env, в котором необходимо прописать описание переменных окружения(скопируйте и вставьте следующий код в файл):
```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
3. Откройте приложение Docker и из директории проекта infa/ запустите docker-compose командой
```
docker-compose up
```
4. Выполните миграции: 
```
docker-compose exec web python manage.py makemigrations
```
```
docker-compose exec web python manage.py migrate
```
5. Создайте суперпользователя 
```docker-compose exec web python manage.py createsuperuser
```
6. Соберите статику
```
docker-compose exec web python manage.py collectstatic --no-input
```
7. Теперь приложение доступно по адресу http://localhost
8. Для наполнения БД из фикстура, из директории проекта infa/ выполните команды:
- скопирует файл с БД fixtures.json в контейнер
```
docker cp fixtures.json <web container id>:app/
``` 
- загрузит данные БД из скопированного контейнер файла
```
docker-compose exec web python manage.py loaddata fixtures.json
```

# Примеры возможных запросов
**GET получить информацию о произведении по id**<br>
`http://127.0.0.1:8000/api/v1/titles/{titles_id}/`
<details><summary>Response 200 удачное выполнение запроса</summary>
{<br>
  "id": 0,<br>
  "name": "string",<br>
  "year": 0,<br>
  "rating": 0,<br>
  "description": "string",<br>
  "genre": [<br>
      {<br>
        "name": "string",<br>
        "slug": "string"<br>
      }<br>
  ],<br>
  "category": {<br>
  "name": "string",<br>
  "slug": "string"<br>
  }<br>
}
</details>
<details><summary>Response 404 объект не найден</summary>
{<br>
  "detail": "Страница не найдена."<br>
}
</details>

**POST добавление нового отзыва**<br>
`http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/`
<details><summary>Request</summary>
{<br>
"text": "string",<br>
"score": 1<br>
}
</details>
<details><summary>Response 201 удачное выполнение запроса</summary>
{<br>
  "id": 0,<br>
  "text": "string",<br>
  "author": "string",<br>
  "score": 1,<br>
  "pub_date": "2019-08-24T14:15:22Z"<br>
}
</details>
<details><summary>Response 400 отсутсвует обязательное поле или оно не найдено</summary>
{<br>
  "score": [<br>
      "Обязательное поле."<br>
  ]<br>
}
</details>
<details><summary>Response 401 необходим JWT-токен</summary>
{<br>
  "detail": "Учетные данные не были предоставлены."<br>
}
</details>
<details><summary>Response 404 произведение не найдено</summary>
{<br>
  "detail": "Страница не найдена."<br>
}
</details>

# Авторы
Екатерина Атабекова<br>
Алексей Трофимов<br>
Александр Куликов<br>

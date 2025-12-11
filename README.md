README.md (АлмаГид API)

AlmaGid API — Backend сервис (FastAPI + PostgreSQL + Docker)

Бұл проект — тур-агенттіктер мен хостелдерді басқаруға арналған серверлік платформа.
Пайдаланушылар тіркеліп, авторизациядан өтеді, өз профилін басқара алады, хостелдер мен агенттіктер қосады, өңдейді және жояды.

Қолданылған технологиялар
	•	FastAPI — негізгі backend фреймворк
	•	PostgreSQL — мәліметтер базасы
	•	SQLAlchemy — ORM
	•	Docker + docker-compose — толық контейнерлеу
	•	JWT (JOSE) — авторизация
	•	Passlib — пароль хэштеу
	•	Static file storage — суреттерді жүктеу
	•	Redis (опционалды) — кэш

⸻

1. Жобаны іске қосу

Қажет:
	•	Docker
	•	Docker Compose

Іске қосу командасы

docker compose up --build

Сервер сілтемелері:

Қызмет	URL
API	http://localhost:8000
Swagger UI	http://localhost:8000/docs
Static files	http://localhost:8000/static
Uploads (картинки)	/static/uploads/…
Avatars	/static/avatars/…


⸻

2. ENV конфигурациясы

docker-compose.yml ішінде автоматты түрде орнатылған.

Егер .env қолдансаңыз:

DATABASE_URL=postgresql://postgres:postgres@db:5432/almagid
JWT_SECRET=change_me_secret_key


⸻

3. МБ миграция және құрылымы

Кестелер
	•	users
	•	places
	•	hostels

Негізгі байланыстар

User (1) — (N) Place  
User (1) — (N) Hostel


⸻

4. API құжаттамасы

Swagger:
➡ http://localhost:8000/docs

Авторизация

POST /auth/register

{
  "full_name": "Test User",
  "phone": "87001112233",
  "email": "test@mail.com",
  "password": "1234"
}

POST /auth/login

{
  "email": "test@mail.com",
  "password": "1234"
}

Жауабы:

{"access_token": "<jwt>"}


⸻

5. Пайдаланушы профилі

GET /me

JWT арқылы ағымдағы пайдаланушыны қайтарады.

PUT /me

Form-data:

full_name
email
phone

POST /me/avatar

Файл жүктеу:

avatar: <image>

Жүктелген сурет сақталады:

/static/avatars/<id_timestamp>.jpg


⸻

6. Тур-агенттіктер API (places)

GET /places

Барлық агенттіктер тізімі

GET /places/my

Тек ағымдағы пайдаланушының агенттіктері

POST /places

Form-data:

name
location
price_text
rating
description
image (optional)

PUT /places/{id}

DELETE /places/{id}

⸻

7. Хостелдер API (hostels)

GET /hostels

GET /hostels/my

POST /hostels

PUT /hostels/{id}

DELETE /hostels/{id}

Толық функционал places сияқты.

⸻

8. Docker құрылымы

docker-compose.yml

version: "3.9"

services:
  api:
    build: .
    container_name: alma_api
    ports:
      - "8000:8000"
    volumes:
      - ./static:/app/static
    depends_on:
      - db

  db:
    image: postgres:15
    container_name: alma_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: almagid
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

Dockerfile

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


⸻

9. Тесттер (мысал)

1) Тіркелу

curl -X POST http://localhost:8000/auth/register \
-H "Content-Type: application/json" \
-d '{"full_name":"Aaa", "phone":"111", "email":"t@t.com", "password":"1234"}'

2) Аватар жүктеу

curl -X POST -H "Authorization: Bearer <token>" \
-F "avatar=@me.png" \
http://localhost:8000/me/avatar


⸻

10. Талаптар сәйкестігі

Талап	Статус
Backend бар	✔
ДБ PostgreSQL	✔
Миграция/Модельдер	✔
Docker контейнерлеу	✔
CRUD толық	✔
Авторизация	✔
Сурет жүктеу	✔
Тесттер	✔
README	✔


⸻

11. Қорытынды

Жоба толықтай бірінші бөлімнің талаптарына сәйкес жүзеге асырылды.
FastAPI + PostgreSQL + Docker негізіндегі толық жұмыс істейтін backend дайын.

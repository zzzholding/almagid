README.md – AlmaGid Backend
Жобаның сипаттамасы
AlmaGid — туристік орындар мен хостелдерді басқаруға арналған веб-қызмет.
Жүйеде пайдаланушылар тіркеліп, авторизациядан өтеді, өзінің профилін басқара алады, хостелдер мен орындарды қосады, өңдейді және өшіреді.
Бэкенд FastAPI, мәліметтер базасы PostgreSQL, контейнеризация Docker арқылы жасалған.
 
Мүмкіндіктер (Features)
Пайдаланушы
• Тіркелу
• 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Логин (JWT токен)
• 
• Профиль көру
• 
•  
•  
•  
•  
•  
•  
•  
•  
• Профиль өзгерту
• 
• Аватар жүктеу
• 
 
 
 
 
 
 
 
 
 
Пароль өзгерту
• 
Контент
• Хостелдер CRUD
• 
• Туристік орындар (Places) CRUD
• 
• Суреттерді серверге жүктеу
• 
• 
• Тек иесі ғана өңдей/өшіреді
• 
• 
• 
 
Технологиялар
• Python 3.11
• FastAPI
• PostgreSQL
• SQLAlchemy
• Docker / Docker Compose
• JWT авторизация
• Passlib (пароль хештеу)
 
 
 
Папка құрылымы
 
app/
│── author.py
│── change_password.py
│── db.py
│── hostels.py
│── gidadd.py
│── profile.py
│── models.py
│── schemas_user.py
│── main.py
static/
│── uploads/
│── avatars/
templates/
│── profile.html
│── hostels.html итд
docker-compose.yml
Dockerfile
requirements.txt
README.md
 
Іске қосу нұсқаулығы
1. Репозиторийді жүктеу
git clone <repo_url>
cd project
2. Орнату (Docker)
docker compose up --build
Қызмет іске қосылады:
→ http://localhost:8000
Swagger UI:
→ http://localhost:8000/docs
 
Environment айнымалылары
docker-compose.yml ішінде:
POSTGRES_DB= my_db
POSTGRES_USER= my_user
POSTGRES_PASSWORD=root
JWT_SECRET=change_me_secret_key
 
 
 
 
 
API (Негізгі endpoint-тар)
Аутентификация
Method
Endpoint
Description
POST
/auth/register
Тіркелу
POST
/auth/login
Логин (JWT токен)
Профиль
Method
Endpoint
Description
GET
/me
Профиль ақпаратын алу
PUT
/me
Өңдеу
POST
/me/avatar
Аватар жүктеу
POST
/auth/change_password
Пароль өзгерту
Hostels
Method
Endpoint
GET
/hostels
GET
/hostels/my
POST
/hostels
PUT
/hostels/{id}
DELETE
/hostels/{id}
Places
Method
Endpoint
GET
/places
POST
/places
PUT
/places/{id}
DELETE
/places/{id}
 
Тесттер (curl мысалдары)
1) Тіркелу
curl -X POST http://localhost:8000/auth/register \
-H "Content-Type: application/json" \
-d '{"full_name":"Test","email":"test@mail.com","phone":"123","password":"1234"}'
2) Логин
curl -X POST http://localhost:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"test@mail.com","password":"1234"}'
3) Профильді алу
curl -H "Authorization: Bearer <token>" http://localhost:8000/me
 
 
 
4) Аватар жүктеу
curl -X POST -F "avatar=@photo.png" \
-H "Authorization: Bearer <token>" \
http://localhost:8000/me/avatar
5) Хостел қосу
curl -X POST http://localhost:8000/hostels \
-H "Authorization: Bearer <token>" \
-F "name=Test Hostel" \
-F "location=Almaty" \
-F "price_text=5000" \
-F "rating=5" \
-F "description=Nice place" \
-F "image=@img.png"
 
Мәліметтер базасы (ER Diagram)
• User (1) → (N) Hostels
• User (1) → (N) Places
Table
Description
users
Пайдаланушылар
hostels
Хостелдер
places
Туристік орындар
 
 
 

 
•  Әр user — контент жасаушы.
•  User көптеген Place сала алады.
•  User көптеген Hostel сала алады.
•  Егер user өшірілсе → оның барлық hostels және places бірге өшеді (CASCADE).
 
 
 
Mock және Test деректер
– Жобаға кіретін бастапқы деректерді seed.sql арқылы енгізуге болады
– Mock сервистер қажет емес (жоба жеке автономды)
 
 


 
 
 
 
 
Лог жүргізу
FastAPI автоматты лог жүргізеді
Docker контейнер журналдары:
docker logs alma_api
docker logs alma_db
alma_db     | 2025-12-10 22:00:32.717 UTC [1] LOG:  starting PostgreSQL 15.15 (Debian 15.15-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
alma_db     | 2025-12-10 22:00:32.719 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
alma_db     | 2025-12-10 22:00:32.719 UTC [1] LOG:  listening on IPv6 address "::", port 5432                                                                                  
alma_db     | 2025-12-10 22:00:32.728 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
alma_db     | 2025-12-10 22:00:32.743 UTC [29] LOG:  database system was shut down at 2025-12-10 22:00:09 UTC                                                                  
alma_db     | 2025-12-10 22:00:32.760 UTC [1] LOG:  database system is ready to accept connections                                                                            
Gracefully Stopping... press Ctrl+C again to force
(86f38014926e7d55efa1646b0679923fc23daf9544713969d201a93400b9377c): Bind for 0.0.0.0:8000 failed: port is already allocated
(.venv) PS C:\Users\дон\Desktop\Almagid>
 
Талаптарға сәйкестік
Талап
Статус
Backend толық
✔
Авторизация
✔
Профиль
✔
Hostels CRUD
✔
Places CRUD
✔
Docker
redis
✔
DB
✔
README
✔
Swagger
✔
Тесттер
✔
 
Қорытынды
Жоба толығымен функционалдық және архитектуралық талаптарға сәйкес келеді, контейнерлерде жұмыс істейді, Postgres-ке жалғанады, барлық API жұмыс істейді, Swagger құжаттамасы бар.

# auth_services
## Микросервис авторизации по логину, паролю и SMS (использует sms.ru)

### Технологии

- Python3, Django, DRF
- PostgreSQL 
- Docker, Docker Compose
- Celery, Redis

### Установка и запуск

Открываем терминал, создаём папку, в которой будет располагаться проект и переходим в неё:
```bash
mkdir /ваш/путь
cd /ваш/путь
```
Клонируем репозотирий в эту папку, переходим в папку проекта:
```bash 
git clone https://github.com/DmitriyChubarov/auth_services.git
cd auth_services
```
Создаём .env файл
```bash
DEBUG=1
SECRET_KEY=your_secret_key_here

DB_NAME=auth_db
DB_USER=user
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

SMS_API_KEY=your_sms_api_key_here
SMS_SENDER=auth_service
```

Запускаем Docker на устройстве, после чего запускаем сервис:
```bash
docker compose up --build
```
Сервисом можно пользоваться, удачи!
```bash
http://localhost:8000/api/register/
```



  
### Контакты
- tg: @eeezz_z
- gh: https://github.com/DmitriyChubarov

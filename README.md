# GeoAssist
2020 Hackathon backend part

Проект размещен на арендованном мной под свои цели хостинге, имеющиеся API-endpoints будут работать из коробки

# Локальный запуск

Требования:

Python 3.8, PostgresQL 12

Развертывание:

0. Создание БД

`sudo -u postgres psql`
`create role geo_admin with password 'geo_pass';`
`alter role geo_admin with login;`
`create database geoassist with owner geo_admin;`
    
1.  Необходимо создать виртуальное окружение Python

`python3 -m venv path/to/venv`
`. /path/to/created/venv/bin/activate`
     
2. После клонирования проекта `cd` в директорию и установка зависимостей
`pip3 install -r requirements.txt`
    
3. Создание и применение миграций

`python3 manage.py makemigrations`
`python3 manage.py migrate`

 При возникновении конфликтов миграций:
 https://www.techiediaries.com/resetting-django-migrations/
 
 4. Запуск сервера
 
 `python3 manage.py runserver` - on `localhost:8000'
 `python3 manage.py runserver 0.0.0.0:8000` - on static IP-address
    

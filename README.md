# 5th_KiriKini_back

- 필수

1. kirikini.pem ~/.ssh에 위치
2. secrets.json를 5th-kirikini-back/KiriKini에 위치

- AWS EC2 서버주소

13.124.158.62

- ssh 접속

```
ssh -i ~/.ssh/kirikini.pem ubuntu@13.124.158.62
python manage.py runserver 0:8000
```

- 최신 끼리끼니 새로 받아오기

```
git pull
pip install -r requirements.txt
```

- 버전

Python3.7.1
Django3.0.2

- 마이그레이션 파일 지우기 : 중간에 디비가 수정되었을때(superuser 다시 생성해야함)

```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
(in psql) drop database kirikini;
(in psql) create database kirikini;
python manage.py makemigrations
python manage.py migrate
```

- postgres 리셋

```
sudo su postgres
psql
drop database kirikini;
create database kirikini with owner admin;
\q
exit
```

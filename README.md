# 5th_KiriKini_back

- 필수

1. kirikini.pem ~/.ssh에 위치
2. secrets.json를 5th_KiriKini_back/KiriKini에 위치

- AWS EC2 서버주소

ec2-54-180-8-109.ap-northeast-2.compute.amazonaws.com

- ssh 접속

```
ssh -i ~/.ssh/kirikini.pem ubuntu@ec2-54-180-8-109.ap-northeast-2.compute.amazonaws.com
python manage.py runserver 0:8000
```

- 최신 끼리끼니 새로 받아오기

```
git pull
pip install -r requirements.txt
```

- 변경사항 확인하면서 push하기
```
git add -p

hunk단위로 추가할지 정하기
y : 해당 hunk를 스테이징
n : 추가하지않기
q : 종료
```

- 버전

Python3.7.1

- 마이그레이션 파일 지우기 : 중간에 디비가 수정되었을때(superuser 다시 생성해야함)

```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
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

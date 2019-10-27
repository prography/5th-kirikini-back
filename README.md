# 5th_KiriKini_back

- 필수

1. kirikini.pem ~/.ssh에 위치
2. secrets.json를 5th_KiriKini_back/KiriKini에 위치

- AWS EC2 서버주소

ec2-54-180-8-109.ap-northeast-2.compute.amazonaws.com

- ssh 접속

ssh -i ~/.ssh/kirikini.pem ubuntu@ec2-54-180-8-109.ap-northeast-2.compute.amazonaws.com

- 최신 끼리끼니 새로 받아오기

git pull
pip install -r requirements.txt


- 버전

Python3.7.1

- 마이그레이션 파일 지우기 : 중간에 디비가 수정되었을때

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

find . -path "*/migrations/*.pyc" -delete

python manage.py makemigrations

python manage.py migrate
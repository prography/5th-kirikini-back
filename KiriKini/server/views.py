# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests
import calendar
import datetime
import random
from dateutil import parser

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from .serializers import MealSerializer, UserSerializer, MealRateSerializer
from .models import Meal, User, MealRate
from django.contrib.auth import get_user_model

from .consts import comments

import emoji


User = get_user_model()

KAKAO_APP_ID = "58e2b8578c74a7039a08d2b7455012a1"
KAKAO_REDIRECT_URI = "http://13.124.158.62/kakao_login"
# KAKAO_REDIRECT_URI = "http://localhost:8000/kakao_login"

# FACEBOOK_APP_ID = "650104882182241"
# FACEBOOK_SECRET = "3a1806fcd6db5e023e0d64db3fd17585"
# FACEBOOK_REDIRECT_URI = "https://127.0.0.1:8000/facebook_login"
# FACEBOOK_REST_API = 'http://localhost:8000/rest-auth/facebook/?method=oauth2'

JWT_OPTAIN_URL = 'http://13.124.158.62/api-jwt-auth/'
JWT_VERIFY_URL = 'http://13.124.158.62/api-jwt-auth/verify/'
JWT_REFRESH_URL = 'http://13.124.158.62/api-jwt-auth/refresh/'
# JWT_OPTAIN_URL = 'http://localhost:8000/api-jwt-auth/'
# JWT_VERIFY_URL = 'http://localhost:8000/api-jwt-auth/verify/'
# JWT_REFRESH_URL = 'http://localhost:8000/api-jwt-auth/refresh/'


def index(request):
    return render(request, 'index.html')


def privacy(request):
    return render(request, 'privacy.html')


@csrf_exempt
def email_register(request):
    body = json.loads(request.body)
    user_email = body['email']
    password = body['password']

    user = User.objects.filter(email=user_email)
    if not user:
        user_data = {
            'email': user_email,
            'username': user_email,
            'password': password
        }
        user = UserSerializer(data=user_data, partial=True)
        if user.is_valid():
            user.save()
            print("user created")
        else:
            print("error", user.errors)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        jwt_data = {
            'email': user_email,
            'password': password  # todo: user 객체로 넣기?
        }
        jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
        print("jwt ", jwt)
        jwt_access_token = jwt['access']
        jwt_refresh_token = jwt['refresh']
        data = {
            'jwt_access_token': jwt_access_token,
            'jwt_refresh_token': jwt_refresh_token
        }

        return JsonResponse(data=data, status=status.HTTP_200_OK)
    else:  # 해당 이메일을 가진 계정이 존재하는 경우
        print("user_email already exists")
        return Response(status=status.HTTP_302_FOUND)


@csrf_exempt
def email_login(request):
    body = json.loads(request.body)

    user_email = body['email']
    password = body['password']

    user = User.objects.filter(email=user_email)
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        user = authenticate(request, username=user_email, password=password)
        if not user:  # 메일은 존재하나 비밀번호가 틀린 경우
            return Response(status=status.HTTP_404_FOUND)
        else:  # 로그인 성공
            jwt_data = {
                'email': user_email,
                'password': password  # todo: user 객체로 넣기?
            }
            jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
            print("jwt ", jwt)
            jwt_access_token = jwt['access']
            jwt_refresh_token = jwt['refresh']
            data = {
                'jwt_access_token': jwt_access_token,
                'jwt_refresh_token': jwt_refresh_token
            }
            return JsonResponse(data=data, status=status.HTTP_200_OK)


@csrf_exempt
def auto_login(request):  # 앱에서 jwt가 있으면 자동로그인한다
    token = json.loads(request.body)
    jwt_access_token = token['jwt_access_token']
    jwt_refresh_token = token['jwt_refresh_token']
    email = token['email']
    print("jwt_access:", jwt_access_token)
    print("jwt_refresh:", jwt_refresh_token)
    print("email:", email)

    data = {'token': jwt_access_token}
    jwt_ok = requests.post(JWT_VERIFY_URL, data)
    print("jwt_ok:", jwt_ok)
    if jwt_ok.status_code == status.HTTP_200_OK:
        user = User.objects.filter(email=email)
        if not user:
            error = "소셜로그인을 해주세요"
            return JsonResponse(data=error, status=status.HTTP_401_UNAUTHORIZED, safe=False)

        return JsonResponse(data, status=status.HTTP_200_OK)

    data = {'refresh': jwt_refresh_token}
    # jwt가 무효하다면 refresh token을 이용해 access token 재발급
    result = requests.post(JWT_REFRESH_URL, data)
    print("result: ", result.json())

    if result.status_code == status.HTTP_401_UNAUTHORIZED:  # refresh token도 만료됬다면 소셜로그인 재유도
        error = "소셜로그인을 해주세요"
        return JsonResponse(data=error, status=status.HTTP_401_UNAUTHORIZED)
    else:
        new_jwt_access_token = result.json()['access']
        print("new jwt:", new_jwt_access_token)
        # 새 access token 반환
        return JsonResponse(data=new_jwt_access_token, status=status.HTTP_201_CREATED, safe=False)


@csrf_exempt
def kakao_login(request):  # 앱에서 JWT가 없는경우 소셜 사이트의 토큰을 받아서 서버에 인증 후 토큰 반환
    token = json.loads(request.body)
    print(token)
    access_token = token['access_token']
    refresh_token = token['refresh_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': "application/x-www-form-urlencoded; charset=-8"
    }
    validate_token = requests.get(
        "https://kapi.kakao.com/v1/user/access_token_info",
        headers=headers
    )
    if validate_token.status_code == status.HTTP_200_OK:
        try:
            user_email = requests.get(
                "https://kapi.kakao.com/v2/user/me", headers=headers).json()['kakao_account']['email']
        except KeyError:
            result = requests.get(
                f"https://kapi.kakao.com/oauth/authorize?client_id={KAKAO_APP_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code&scope=account_email").json()
            user_email = requests.post(
                "https://kapi.kakao.com/v2/user/me", headers=headers, data=data).json()['email']

        user = User.objects.filter(email=user_email)
        if not user:
            user_data = {
                'email': user_email,
                'username': user_email,
                'password': user_email
            }
            user = UserSerializer(data=user_data, partial=True)
            if user.is_valid():
                user.save()
                print("user created")
            else:
                print("error", user.errors)

        jwt_data = {
            'email': user_email,
            'password': user_email  # todo: user 객체로 넣기?
        }
        jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
        print("jwt ", jwt)
        jwt_access_token = jwt['access']
        jwt_refresh_token = jwt['refresh']
        data = {
            'jwt_access_token': jwt_access_token,
            'jwt_refresh_token': jwt_refresh_token
        }

        return JsonResponse(data, status=status.HTTP_200_OK)

    else:
        data = {'error': '소셜로그인을 다시 진행해주세요.'}
        return JsonResponse(data, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
def facebook_login(request):
    body = dict(request.POST)
    access_token = body['access_token']
    # refresh_token = body['refresh_token']

    params_debug = {
        "input_token": access_token,
        "access_token": f'{FACEBOOK_APP_ID}|{FACEBOOK_SECRET}'
    }
    debug = requests.get(
        "https://graph.facebook.com/debug_token", params=params_debug)
    if debug.status_code == status.HTTP_200_OK:

        params_user = {
            "fields": ["email"],
            "access_token": access_token
        }
        user_fb_data = requests.get(
            "https://graph.facebook.com/me", params=params_user).json()
        user_email = user_fb_data['email']
        user = UserSerializer(data=user_data, partial=True)
        if user.is_valid():
            user.save()
            print("user created")
        else:
            print("error", user.errors)

    jwt_data = {
        'email': user_email,
        'password': access_token[0:10]
    }
    jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
    access_token = jwt['access']
    refresh_token = jwt['refresh']
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def create_meal(request):
    if request.method == 'GET':
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        body = json.loads(request.body)

        meal_data = {
            'user': request.user.id,
            'mealType': body['mealType'],
            'gihoType': body['gihoType'],
            'picURL': body['picURL'],
            'created_at': parser.parse(body['created_at']),
            # todo: 지금은 테스트용으로 현재 점수만 받지만 나중에 평균점수 계산해주기
            'average_rate': body['rating']
        }
        print("meal_data ", meal_data)

        meal_serializer = MealSerializer(data=meal_data)
        if meal_serializer.is_valid():
            meal_serializer.save()

            meal_id = Meal.objects.latest('id').id
            meal_rate_data = {
                'user': request.user.id,
                'meal': meal_id,
                'rating': body['rating']
            }
            meal_rate_serializer = MealRateSerializer(data=meal_rate_data)
            if meal_rate_serializer.is_valid():
                meal_rate_serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                print("error: ", meal_rate_serializer.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print("error: ", meal_serializer.errors)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def load_yesterday_rating(request):
    user_id = request.user.id
    now = timezone.now() - datetime.timedelta(days=1)
    date = now.strftime("%Y-%m-%d")

    meals = Meal.objects.filter(user=user_id, created_at__contains=date)
    yesterday_rating = None

    try:
        yesterday_rating_sum = 0
        for meal in meals:
            yesterday_rating_sum += meal.average_rate

        yesterday_rating = round(yesterday_rating_sum / meals.count(), 2)
    except Exception as err:
        print(err)
        return JsonResponse(err)

    return JsonResponse(yesterday_rating, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
def load_today_meal(request):
    user_id = request.user.id
    now = timezone.now()
    date = now.strftime("%Y-%m-%d")

    meals = Meal.objects.filter(
        user=user_id, created_at__contains=date).order_by('created_at')
    meals = list(meals.values())

    return JsonResponse(meals, status=status.HTTP_200_OK, safe=False)


@api_view(['GET', 'POST'])
def load_month_meal(request):
    def _get_week_of_month(tgtdate, meals_by_weeks):
        days_this_month = calendar.mdays[tgtdate.month]
        for i in range(1, days_this_month):
            d = datetime.date(tgtdate.year, tgtdate.month, i)
            if d.day - d.weekday() > 0:
                startdate = d
                break

        result = (tgtdate - startdate).days // 7 + 1
        meals_by_weeks[result]["range"].append()
        return result

        # if type(date) == str:
        #     date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        # cal_object = calendar.Calendar(0)
        # month_calendar_dates = cal_object.itermonthdates(date.year, date.month)
        # day_of_week = 1
        # week_number = 1

        # date = datetime.datetime.strftime(date, "%Y-%m-%d")

        # for day in month_calendar_dates:
        #     if day_of_week > 7:
        #         week_number += 1
        #         day_of_week = 1
        #     if date == (datetime.datetime.strftime(day, "%Y-%m-%d")):
        #         break
        #     else:
        #         day_of_week += 1

        # return week_number

    month = json.loads(request.body)["month"]

    if len(str(month)) == 1:
        month = "0" + str(month)

    user_id = request.user.id
    now = timezone.now()
    year = now.strftime("%Y")
    date = year + '-' + month

    meals = Meal.objects.filter(user=user_id, created_at__contains=date)
    meals = list(meals.values())

    meals_by_weeks = {
        1: {
            "range": [],
            "meals": []
        },
        2: {
            "range": [],
            "meals": []
        },
        3: {
            "range": [],
            "meals": []
        },
        4: {
            "range": [],
            "meals": []
        },
        5: {
            "range": [],
            "meals": []
        }
    }
    for meal in meals:
        week = _get_week_of_month(meal['created_at'], meals_by_weeks)
        meal['day'] = meal['created_at'].weekday()
        meals_by_weeks[week].append(meal)

    return JsonResponse(meals_by_weeks, status=status.HTTP_200_OK, safe=False)


@api_view(['GET', 'POST'])
def rate_meal(request):
    user_id = request.user.id

    if request.method == 'GET':  # 채점할 끼니를 불러온다
        my_mealrates = MealRate.objects.filter(user_id=user_id)
        mealrates = MealRate.objects.all().exclude(user_id=user_id)

        meals_rated = list()
        for mealrate in my_mealrates:
            meals_rated.append(mealrate.meal_id)

        meals_not_rated = list()
        for mealrate in mealrates:
            if mealrate.meal_id not in meals_rated:
                meals_not_rated.append(mealrate.meal_id)

        meals_not_rated = Meal.objects.filter(id__in=meals_not_rated)
        meals_not_rated = list(meals_not_rated.values())

        return JsonResponse(meals_not_rated, status=status.HTTP_200_OK, safe=False)

    elif request.method == 'POST':  # todo: 끼니 채점 정보를 앱으로부터 받아온다
        body = json.loads(request.body)

        meal_to_rate = {
            'user': user_id,
            'meal': body['meal'],
            'rating': body['rating']
        }

        meal_rate_serializer = MealRateSerializer(data=meal_to_rate)
        if meal_rate_serializer.is_valid():
            meal_rate_serializer.save()
            meal = Meal.objects.get(id=body['meal'])
            rate_counts = MealRate.objects.filter(
                meal_id=body['meal']).count()

            print("rate_counts", rate_counts)

            meal.average_rate = (meal.average_rate +
                                 body['rating']) / rate_counts
            meal.save()
            return Response(status=status.HTTP_200_OK)

        else:
            print("error: ", meal_rate_serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def load_since_meal_info(request):
    user_id = request.user.id
    now = timezone.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

    since_info = {
        'meal': 0,
        'coffee': 0,
        'drink': 0,
    }

    # latest_meal = Meal.objects.filter(
    #     user=user_id, gihoType=None).latest('created_at')

    # latest_coffee = Meal.objects.filter(
    #     user=user_id, gihoType=0).latest('created_at')

    # latest_drink = Meal.objects.filter(
    #     user=user_id, gihoType=1).latest('created_at')

    # if latest_meal:
    #     for meal in latest_meal:
    #         print(2)
    #         meal_time = meal['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    #         delta_seconds = int((now - meal_time).total_seconds())
    #         since_info["meal"] = delta_seconds

    # if latest_coffee:
    #     for coffee in latest_coffee:
    #         coffee_time = coffee['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    #         delta_seconds = int((now - coffee_time).total_seconds())
    #         since_info["coffee"] = delta_seconds

    # if latest_drink:
    #     for drink in latest_drink:
    #         drink_time = drink['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    #         delta_seconds = int((now - drink_time).total_seconds())
    #         since_info["drink"] = delta_seconds

    meals = Meal.objects.filter(user=user_id).order_by('-created_at')
    meals = list(meals.values())

    for meal in meals:
        meal_time = meal['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        meal_time = datetime.datetime.strptime(meal_time, '%Y-%m-%d %H:%M:%S')
        delta_seconds = int((now - meal_time).total_seconds())

        if meal['gihoType'] == 0 and since_info['coffee'] == 0:  # 커피
            since_info['coffee'] = delta_seconds
        elif meal['gihoType'] == 1 and since_info['drink'] == 0:  # 술
            since_info['drink'] = delta_seconds
        elif meal['gihoType'] == None and since_info['meal'] == 0:  # 끼니
            since_info['meal'] = delta_seconds

    print(f'since_info:{since_info}')

    return JsonResponse(since_info, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def load_week_report(request):
    def _get_start_end_day_of_week(date):
        start = date - datetime.timedelta(days=date.weekday())
        end = start + datetime.timedelta(days=6)
        return timezone.make_aware(parser.parse(start.strftime("%Y-%m-%d"))), (timezone.make_aware(parser.parse(end.strftime("%Y-%m-%d")) + datetime.timedelta(hours=23, seconds=3599)))

    def _load_previous_week_rating():
        user_id = request.user.id
        previous_week = timezone.now() - datetime.timedelta(days=7)
        date = previous_week.strftime("%Y-%m-%d")
        previous_week_start_day, previous_week_end_day = _get_start_end_day_of_week(
            previous_week)
        meals = Meal.objects.filter(
            user=user_id, created_at__range=(previous_week_start_day, previous_week_end_day))

        try:
            previous_week_rating_sum = 0
            for meal in meals:
                previous_week_rating_sum += meal.average_rate

            previous_week_rating = round(
                previous_week_rating_sum / meals.count(), 2)
            return previous_week_rating
        except Exception as err:
            return print(err)

    def _get_comments(type):
        if type == 'meal':
            if meal_count >= 25:
                return random.choice(comments["meal"]["overeating"])
            elif meal_count >= 16:
                return random.choice(comments["meal"]["compliment"])
            else:
                return random.choice(comments["meal"]["starving"])

        elif type == 'drink':
            if drink_count >= 2:
                return random.choice(comments["drink"]["2"])
            elif drink_count == 1:
                return random.choice(comments["drink"]["1"])
            else:
                return random.choice(comments["drink"]["0"])

        elif type == 'coffee':
            if coffee_count >= 6:
                return random.choice(comments["coffee"]["6"])
            elif coffee_count >= 1:
                return random.choice(comments["coffee"]["5"])
            else:
                return random.choice(comments["coffee"]["0"])

        elif type == 'house':
            return random.choice(comments["house"])
        elif type == 'out':
            return random.choice(comments["out"])
        elif type == 'delivery':
            return random.choice(comments["delivery"])
        elif type == 'simple':
            return random.choice(comments["simple"])

    user_id = request.user.id
    # user_name = request.user_name
    now = timezone.now()
    start_day, end_day = _get_start_end_day_of_week(now)

    meals = Meal.objects.filter(
        user=user_id, created_at__range=(start_day, end_day))
    meals = list(meals.values())

    try:
        week_score = 0
        meal_count = 0
        drink_count = 0
        coffee_count = 0
        score_by_day = [{"count": 0, "score": 0} for _ in range(7)]
        score_by_meal_type = [{"count": 0, "score": 0} for _ in range(4)]

        for meal in meals:
            week_score += meal["average_rate"]
            meal_count += 1

            if meal["gihoType"] == 0:  # 커피
                coffee_count += 1
            elif meal["gihoType"] == 1:  # 술
                drink_count += 1

            if meal["created_at"].weekday() == 0:  # 월
                score_by_day[0]["count"] += 1
                score_by_day[0]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 1:
                score_by_day[1]["count"] += 1
                score_by_day[1]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 2:
                score_by_day[2]["count"] += 1
                score_by_day[2]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 3:
                score_by_day[3]["count"] += 1
                score_by_day[3]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 4:
                score_by_day[4]["count"] += 1
                score_by_day[4]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 5:
                score_by_day[5]["count"] += 1
                score_by_day[5]["score"] += meal["average_rate"]
            elif meal["created_at"].weekday() == 6:
                score_by_day[6]["count"] += 1
                score_by_day[6]["score"] += meal["average_rate"]

            if meal["mealType"] == 0:  # 집밥
                score_by_meal_type[0]["count"] += 1
                score_by_meal_type[0]["score"] += meal["average_rate"]
            elif meal["mealType"] == 1:  # 외식
                score_by_meal_type[1]["count"] += 1
                score_by_meal_type[1]["score"] += meal["average_rate"]
            elif meal["mealType"] == 2:  # 배달
                score_by_meal_type[2]["count"] += 1
                score_by_meal_type[2]["score"] += meal["average_rate"]
            elif meal["mealType"] == 3:  # 간편식
                score_by_meal_type[3]["count"] += 1
                score_by_meal_type[3]["score"] += meal["average_rate"]

        counts_by_meal_type = []
        for i in range(7):
            if score_by_day[i]["count"] > 0:
                score_by_day[i]["score"] = round(
                    score_by_day[i]["score"] / score_by_day[i]["count"], 1)
            counts_by_meal_type.append(score_by_day[i]["count"])
        for i in range(4):
            if score_by_meal_type[i]["count"] > 0:
                score_by_meal_type[i]["score"] = round(
                    score_by_meal_type[i]["score"] / score_by_meal_type[i]["count"], 1)

        week_score = meal_count if meal_count == 0 else round(
            week_score / meal_count, 1)
        avg_meal_count = round(meal_count / 7, 1)

        comment0 = "과도한" if meal_count >= 25 else "적절한" if meal_count >= 16 else "부족한"
        comment1 = "건강한" if drink_count+coffee_count >= 9 else "건강하지 못 한"
        comment2 = None
        comment3 = '다음주도 이번주처럼!' if week_score >= 8 else '다음주는 더 분발하는게 어때?' if week_score >= 4 else '다음주는 사람답게 먹자!'
        comment4 = [_get_comments("meal"), _get_comments(
            "drink"), _get_comments("coffee")]
        comment5 = None

        max_count_by_type = 0
        max_type = None
        for i in range(4):
            if(max_count_by_type < score_by_meal_type[i]["count"]):
                max_count_by_type = score_by_meal_type[i]["count"]
                if i == 0:
                    max_type = "house"
                    comment2 = "집밥"
                elif i == 1:
                    max_type = "out"
                    comment2 = "외식"
                elif i == 2:
                    max_type = "delivery"
                    comment2 = "배달"
                else:
                    max_type = "simple"
                    comment2 = "간편식"

        if max_type:
            comment5 = "집밥을 많이 먹었어요! " if max_type == "house" else "바깥 음식을 좋아하는 당신! " \
                if max_type == "out" else f'배달 음식을 너무 많이 먹고있어요! {emoji.emojize(":warning:")}' \
                if max_type == "delivery" else "간편식을 너무 많이 먹었어요! "
            comment5 += _get_comments(max_type)

        feedback = [
            '끼리니가 이번주 식단을 평가해주지!\n',
            f'총 {meal_count}끼니의 {comment0} 끼니 횟수, \n',
            f'{drink_count}회의 음주, {coffee_count}회의 카페인으로 {comment1} 습관,\n',
            f'{comment2}이 많으며,\n',
            f'건강도 {week_score}에 달하는 당신은 \n\n{comment3}\n',
            comment4,
            # comment5
        ]

        week_report = {
            "week_score": week_score,
            "previous_week_score": _load_previous_week_rating(),
            "avg_meal_count": avg_meal_count,
            "meal_count": meal_count,
            "drink_count": drink_count,
            "coffee_count": coffee_count,
            "score_by_day": score_by_day,
            "score_by_meal_type": score_by_meal_type,
            "counts_by_meal_type": counts_by_meal_type,
            "feedback": feedback
        }

        return JsonResponse(week_report, status=status.HTTP_200_OK)

    except Exception as err:
        print(err)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# <주간 레포트>

# ooo님의 지난 7일간의 식단 레포트야.
# ///선그래프
# 이번주의 당신은 총 n회의 끼니를 먹었어![코멘트]
# ///막대그래프(술.커피 총 2개)
# 당신의 음주 횟수는 n회이고 [코멘트]
# 커피는 n회 마셨어[코멘트]
# ///원그래프(식단형태)
# 배달 n회, 집밥 n회, 외식 n회, 간편식 n회 로
# [코멘트]

# 끼리니가 너의 이번주 식단을 평가해주지!

# 총 n끼니의 (과도한 / 적절한 / 부족한) 끼니 횟수,
# n회의 음주 n회의 카페인으로 (건강한 / 건강하지 못한) 습관,
# (간편식 / 배달 / 집밥 / 외식) 이 많으며
# 건강도 (n)점에 달하는 당신은
# [점수에 따른 건강도 코멘트], (8점 이상 - 다음주도 이번주처럼! / 4-7점 다음주는 더 분발하는게 어때? / 0-3점 – 다음주는 사람답게 먹자!)

# <끼니 횟수 코멘트>

# (끼니 15회 이하 - 굶주림)
# -지금처럼 조금 먹다가는 살과 함께 건강도 같이 빠질거에요
# -끼니 좀 거르지마! 또 거르면 끼리니가 너를 걸러낼거야!
# -이번주도 제대로 못 챙겨 먹은 당신. 다음주에는 끼리끼니와 함께 더 열심히 먹어봅시다!

# (끼니 16~24회 - 칭찬)
# -이대로 라면 100살까지는 거뜬히 살 수 있을거에요
# -이대로 라면 건강 걱정은 없을겁니다!
# -끼니를 거르지 않는 당신은 이 시대의 건강왕!

# (끼니 25회 이상 - 과식)
# -지금처럼 많이 먹다가는 몸무게 앞자리가 달라지는 경험을 하실거에요
# -대부분은 살기 위해 먹는데, 당신은 먹기 위해 사는 것이 확실하네요
# -또..또..먹었어요,,? 그만…그만…그만…!!

# <술 코멘트>

# (주 2회이상)
# -당신의 간이 지쳐가고 있어요
# -간이 욕한다 욕해,,
# -너는 간이 3개니?
# -이번주는 물보다 술을 많이 마셨네! 대단하다 친구야!
# -맨날 술이야~ 맨날 술이야~
# -매일 술 퍼마시는 너를 보면 끼리니는 술퍼져..

# (1회)
# -이번주 당신의 음주는 아주 바람직하네요!
# -그래 일주일에 한 번은 괜찮지!
# (0회)
# -이번주는 금주에 성공했어요! 짝짝짝!
# -이번주 금주 기념으로 끼리니가 술 한잔 살게~! 밥 한 술~!

# <커피 코멘트>
# (주 6회이상)
# -당신은 정말 물 마시듯 커피를 드시네요
# -뭐든지 적당히 좀!
# -정신을 깨기 위해서 커피를 마시는건데 이렇게 마시다 머리가 깨지겠어요
# -이번주는 물보다 커피를 더 많이 마셨겠네요
# -이번주에 마신 카페인은 당신을 폐인으로 만들 수도 있는 양이었어요…

# (1~5회)
# -이번주 당신의 카페인의 엑셀런트! 적당한 카페인은 몸에도 좋다네요!
# -이번주 마신 카페인 정도는 끼리니가 봐줄게!
# (0회)
# -이번주 당신은 금카(0카페인)에 성공했어요!
# -카페인이 필요 없는 당신, 건강은 너의 것!
# <음식 형태>

# (외식) 바깥 음식을 좋아하는 당신[코멘트]
# -이번주는 외식이 많았어요! 맛은 있지만 건강에는 안좋을 수도 있어요..내 지갑 사정에도 안좋고..
# -외식을 하더라도 샐러드나 생선과 같이 건강한 외식에 도전해보는 것은 어떨까요?
# (배달) 배달 음식을 너무 많이 먹고 있어요(경고등 이모티콘)[코멘트]

# -배달의민족이 진짜 우리 민족은 아니에요. 다음주에는 건강한 집밥에 도전해보는 것은 어떨까요?
# -자극적인 배달 음식을 많이 먹었다면 이제 건강식에 도전해보는 것은 어떨까요?
# -치킨, 피자, 족발, 보쌈 중 2개 이상을 먹었다면 배민과 잠시 이별해야 할 시간이에요..

# (집밥) 집밥을 많이 먹었어요![코멘트]
# -집밥을 많이 먹었다는 것은 좋은 징조에요! 집밥을 먹더라도 다양한 영양소를 먹어야 하는 것 알죠?
# -집밥을 애정하는 당신! 다음주에는 더 다양한 요리에 도전해보는 것은 어떨까요?

# (간편식) 간편식을 너무 많이 먹었어요[코멘트]
# -간편함이 건강을 보장하지는 않는답니다!
# -편하게 먹으려는 자는 편치 못한 건강을 얻을 것이다
# -빠르게 먹는 것을 좋아하다가 빠르게 갈 수도 있어요!

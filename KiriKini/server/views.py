# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests
from dateutil import parser
import calendar
import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

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
User = get_user_model()

KAKAO_APP_ID = "58e2b8578c74a7039a08d2b7455012a1"
KAKAO_REDIRECT_URI = "http://ec2-52-78-23-61.ap-northeast-2.compute.amazonaws.com/kakao_login"
# KAKAO_REDIRECT_URI = "http://localhost:8000/kakao_login"

FACEBOOK_APP_ID = "650104882182241"
FACEBOOK_SECRET = "3a1806fcd6db5e023e0d64db3fd17585"
FACEBOOK_REDIRECT_URI = "https://127.0.0.1:8000/facebook_login"
FACEBOOK_REST_API = 'http://localhost:8000/rest-auth/facebook/?method=oauth2'

JWT_OPTAIN_URL = 'http://ec2-52-78-23-61.ap-northeast-2.compute.amazonaws.com/api-jwt-auth/'
JWT_VERIFY_URL = 'http://ec2-52-78-23-61.ap-northeast-2.compute.amazonaws.com/api-jwt-auth/verify/'
JWT_REFRESH_URL = 'http://ec2-52-78-23-61.ap-northeast-2.compute.amazonaws.com/api-jwt-auth/refresh/'
# JWT_OPTAIN_URL = 'http://localhost:8000/api-jwt-auth/'
# JWT_VERIFY_URL = 'http://localhost:8000/api-jwt-auth/verify/'
# JWT_REFRESH_URL = 'http://localhost:8000/api-jwt-auth/refresh/'


def index(request):
    return render(request, 'index.html')


def privacy(request):
    return render(request, 'privacy.html')


@csrf_exempt
def email_login(request):
    body = dict(request.POST)

    return Response(status=status.HTTP_200_OK)


@csrf_exempt
def auto_login(request):  # 앱에서 jwt가 있으면 자동로그인한다
    # jwt가 유효하지 않다면 재발급하기 위해 앱에서 access token과 refresh token을 둘 다 보냄
    body = dict(request.POST)
    token = None

    for t in body.keys():
        token = t

    token = json.loads(token)
    jwt_access_token = token['jwt_access_token']
    jwt_refresh_token = token['jwt_refresh_token']
    print("jwt_access:", jwt_access_token)
    print("jwt_refresh:", jwt_refresh_token)

    data = {'token': jwt_access_token}
    jwt_ok = requests.post(JWT_VERIFY_URL, data)
    print("jwt_ok:", jwt_ok)
    if jwt_ok.status_code == status.HTTP_200_OK:
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
    body = dict(request.POST)
    token = None
    for t in body.keys():
        token = t

    token = json.loads(token)
    access_token = token['access_token']
    refresh_token = token['refresh_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': "application/x-www-form-urlencoded; charset=utf-8"
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
                'accessToken': access_token,
                # 'refreshToken': refresh_token,
                # 'password': access_token[:10]
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
            'password': user_email
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


@api_view(['GET'])
def detail_user(request, pk):
    # permissions = (permissions.IsAuthenticatedOrReadOnly,)
    """
    """
    try:
        users = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=400)
    if request.method == 'GET':
        serializer = UserSerializer(meals)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def create_meal(request):
    if request.method == 'GET':
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        body = dict(request.POST)
        for t in body.keys():
            body = json.loads(t)

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


@api_view(['GET', 'PUT', 'DELETE'])
def detail_meal(request, pk):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly, )
    """
    """
    try:
        meals = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return Response(status=400)

    if request.method == 'GET':
        serializer = MealSerializer(meals)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = MealSerializer(meals, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        meals.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def load_today_meal(request):
    user_id = request.user.id
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")

    meals = Meal.objects.filter(user=user_id, created_at__contains=date)
    meals = list(meals.values())

    return JsonResponse(meals, status=status.HTTP_200_OK, safe=False)


@api_view(['GET', 'POST'])
def load_month_meal(request):
    def _get_week_of_month(date):
        if type(date) == str:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        cal_object = calendar.Calendar(0)
        month_calendar_dates = cal_object.itermonthdates(date.year, date.month)
        day_of_week = 1
        week_number = 1

        for day in month_calendar_dates:
            if day_of_week > 7:
                week_number += 1
                day_of_week = 1
            if date == day:
                break
            else:
                day_of_week += 1

        return week_number

    body = dict(request.POST)
    month = None

    for t in body.keys():
        month = json.loads(t)

    user_id = request.user.id
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    date = year + '-' + str(month['month'])

    meals = Meal.objects.filter(user=user_id, created_at__contains=date)
    meals = list(meals.values())

    meals_by_weeks = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    for meal in meals:
        week = _get_week_of_month(meal['created_at'])-1
        meal['day'] = meal['created_at'].weekday()
        meals_by_weeks[week].append(meal)

    return JsonResponse(meals_by_weeks, status=status.HTTP_200_OK, safe=False)


@api_view(['GET', 'POST'])
def rate_meal(request):
    user_id = request.user.id

    if request.method == 'GET':  # 채점할 끼니를 불러온다
        mealrates = MealRate.objects.filter(~Q(user=user_id))
        mealrates = list(mealrates.values())

        meals_not_rated = list()
        for mealrate in mealrates:
            meals_not_rated.append(mealrate.meal)

        meals_not_rated = Meal.objects.filter(id__in=meals_not_rated)
        print("meals_not_rated:", meals_not_rated)
        meals_not_rated = list(meals_not_rated.values())

        return JsonResponse(meals_not_rated, status=status.HTTP_200_OK, safe=False)

    elif request.method == 'POST':  # todo: 끼니 채점 정보를 앱으로부터 받아온다
        body = dict(request.POST)
        for t in body.keys():
            body = json.loads(t)

        meal_to_rate = {
            'user': user_id,
            'meal': body['meal'],
            'rating': body['rating']
        }

        meal_rate_serializer = MealRateSerializer(data=meal_to_rate)
        if meal_rate_serializer.is_valid():
            meal_rate_serializer.save()

            meal = Meal.objects.filter(meal=body['meal'])
            rate_counts = MealRate.objects.filter(meal=body['meal']).length

            meal.average_rate = (meal.average_rate + rating) / rate_counts
            Meal.objects.update(meal)

            return Response(status=status.HTTP_200_OK)
        else:
            print("error: ", meal_rate_serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

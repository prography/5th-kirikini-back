# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json, requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from .serializers import MealSerializer, UserSerializer
from .models import Meal,User
from django.contrib.auth import get_user_model
User = get_user_model()

KAKAO_APP_ID = "58e2b8578c74a7039a08d2b7455012a1"
KAKAO_REST_API = 'http://localhost:8000/rest-auth/kakao/?method=oauth2'
KAKAO_REDIRECT_URI = "http://localhost:8000/kakao_login"

FACEBOOK_APP_ID = "650104882182241"
FACEBOOK_SECRET = "3a1806fcd6db5e023e0d64db3fd17585"
FACEBOOK_REDIRECT_URI = "https://127.0.0.1:8000/facebook_login"
FACEBOOK_REST_API = 'http://localhost:8000/rest-auth/facebook/?method=oauth2'

JWT_OPTAIN_URL = 'http://localhost:8000/api-jwt-auth/'
JWT_VERIFY_URL = 'http://localhost:8000/api-jwt-auth/verify'
JWT_REFRESH_URL = 'http://localhost:8000/api-jwt-auth/refresh'


def index(request):
    return render(request, 'index.html')


def verify_jwt(jwt):
    data = {'token': jwt}
    jwt_ok = requests.request('POST', JWT_VERIFY_URL, data).json()['status']
    if jwt_ok == status.HTTP_200_OK:
        return True
    return False


@csrf_exempt
def auto_login(request): # 앱에서 jwt가 있으면 자동로그인한다
    body = dict(request.POST) # jwt가 유효하지 않다면 재발급하기 위해 앱에서 access token과 refresh token을 둘 다 보냄
    print(body)
    jwt_access_token = body['jwt_access_token']
    jwt_refresh_token = body['jwt_refresh_token']

    if verify_jwt(jwt_access_token): # jwt가 유효하다면 해당 유저를 인증 처리 한다(?)
        # token = AccessToken(jwt_access_token)
        # user = User.objects.get(token['user_id'])
        return JsonResponse(status=status.HTTP_200_OK)

    data = {'refresh': jwt_refresh_token}
    result = requests.POST(JWT_REFRESH_URL, data).json() # jwt가 무효하다면 refresh token을 이용해 access token 재발급

    if result == status.HTTP_401_UNAUTHORIZED: # refresh token도 만료됬다면 소셜로그인 재유도
        error = "소셜로그인을 해주세요"
        return JsonResponse(data = error, status=status.HTTP_401_UNAUTHORIZED)
    
    new_jwt_access_token = result['access']
    return JsonResponse(data = new_jwt_access_token, status=status.HTTP_201_CREATED) # 새 access token 반환
    

@csrf_exempt
def kakao_login(request):  # 앱에서 JWT가 없는경우 소셜 사이트의 토큰을 받아서 서버에 인증 후 토큰 반환
    body = dict(request.POST)
    print(body)
    access_token = body['access_token'][0]
    refresh_token = body['refresh_token'][0]

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': "application/x-www-form-urlencoded; charset=utf-8"
    }
    validate_token = requests.get("https://kapi.kakao.com/v1/user/access_token_info", headers=headers)
    if validate_token.status_code == status.HTTP_200_OK:
        try:
            user_email = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers).json()['kakao_account']['email']
        except KeyError:
            result = requests.get(f"https://kapi.kakao.com/oauth/authorize?client_id={KAKAO_APP_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code&scope=account_email").json()
            user_email = requests.post("https://kapi.kakao.com/v2/user/me", headers=headers, data=data).json()['email']
        
        user = User.objects.filter(email=user_email)
        if not user:
            user_data = {
                'email': user_email,
                'username': user_email,
                'accessToken': access_token,
                'refreshToken': refresh_token,
                'password': access_token[:10]
            }
            user = UserSerializer(data=user_data, partial=True)
            if user.is_valid():
                user.save()
                print("user created")
            else:
                print("error", user.errors)

        jwt_data = {
            'email': user_email,
            'password': access_token[:10]
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
    debug = requests.get("https://graph.facebook.com/debug_token", params=params_debug)
    if debug.status_code == status.HTTP_200_OK:

        params_user = {
            "fields": ["email"],
            "access_token": access_token
        }
        user_fb_data = requests.get("https://graph.facebook.com/me", params=params_user).json()
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


@api_view(['GET','POST'])
def create_meal(request):
    """
    """
    if request.method == 'GET':
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer == MealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

      
@api_view(['GET','PUT','DELETE'])
def detail_meal(request,pk):
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
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        meals.delete()
        return Response(status=204)
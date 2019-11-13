# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json, requests

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.decorators import api_view, permission_classes, authentication_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from .serializers import MealSerializer, UserSerializer
from .models import Meal
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
    access_token = body['access_token']
    refresh_token = body['refresh_token']

    if verify_jwt(access_token): # jwt가 유효하다면 해당 유저를 인증 처리 한다(?)
        # token = AccessToken(access_token)
        # user = User.objects.get(token['user_id'])
        return Response(status=status.HTTP_200_OK)

    data = {'refresh': refresh_token}
    result = requests.POST(JWT_REFRESH_URL, data).json() # jwt가 무효하다면 refresh token을 이용해 access token 재발급

    if result == status.HTTP_401_UNAUTHORIZED: # refresh token도 만료됬다면 소셜로그인 재유도
        error = "소셜로그인을 해주세요"
        return Response(data = error, status=status.HTTP_401_UNAUTHORIZED)
    
    new_access_token = result['access']
    return Response(data = new_access_token, status=status.HTTP_201_CREATED) # 새 access token 반환
    
    
@csrf_exempt
@renderer_classes((JSONRenderer))
def kakao_login(request):  # 앱에서 JWT가 없는경우 소셜 사이트의 토큰을 받아서 서버에 인증 후 토큰 반환
    # {"refreshTokenExpiresAt":"2020-01-12T13:24:25","accessTokenExpiresAt":"2019-11-14T01:24:25","refreshToken":"bTRQzNCXLSu7SAi9RilfM71p2XOnPdQSgVUfuQopdXYAAAFuYwFsjg","accessToken":"rVSnN9t6R_sXwAgMi5TKgO0ZBK-xknEOTnA1MAopdXYAAAFuYwFsjw"}
    # access_token = body['access_token']
    # refresh_token = body['refresh_token']

    # headers = {
    #     'Authorization': f'Bearer {access_token}',
    #     'Content-type': "application/x-www-form-urlencoded; charset=utf-8"
    # }
    # validate_token = requests.get("https://kapi.kakao.com/v1/user/access_token_info", headers=headers)
    # if validate_token.status_code == status.HTTP_200_OK:
    #     data = {'property_keys': ["kakao_account.email"]}
    #     user_email = requests.post("https://kapi.kakao.com/v2/user/me", headers=headers, data=data).json()['email']

    #     if not user_email:
    #         result = requests.get(f"https://kapi.kakao.com/oauth/authorize?client_id={KAKAO_APP_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code&scope=account_email").json()
    #         user_email = requests.post("https://kapi.kakao.com/v2/user/me", headers=headers, data=data).json()['email']
        
    #     user = User.objects.filter(email=user_email)
    #     if not user:
    #         user_data = {
    #             'email': "abcd@google.com",
    #             'username': "abcd@google.com",
    #             # 'accessToken': access_token,
    #             'refreshToken': refresh_token,
    #         }
    #         user = UserSerializer(data=user_data, partial=True)
    #         if user.is_valid():
    #             user.save()
    #             print("saved!!!!!!!!!!!!!!!")
    #         else:
    #             print("error", user.errors)

    #     jwt_data = {
    #         'username': user_email,
    #         'password': access_token
    #     }
    #     jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
    #     jwt_access_token = jwt['access']
    #     jwt_refresh_token = jwt['refresh']
    #     data = {
    #         'jwt_access_token': jwt_access_token,
    #         'jwt_refresh_token': jwt_refresh_token
    #     }

    #     return Response(data=data, status=status.HTTP_201_CREATED)

    # else:
    #     data = {'error': '소셜로그인을 다시 진행해주세요.'}
    #     return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)


   # code 얻기
    body = dict(request.GET)
    code = body['code'][0]

    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_APP_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }
    tokens = requests.post("https://kauth.kakao.com/oauth/token", data=data, headers=headers).json()
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    data = {
        "access_token": access_token,
        "code": code
    }

    # access_token 얻기
    headers = {
        "Authorization": "Bearer " + access_token
    }
    user_kakao_data = requests.get('https://kapi.kakao.com/v2/user/me', headers=headers).json()  # 카카오톡 서버로 해당 유저의 정보 가져오기
    print("000000000000000")
    print(user_kakao_data)
    print("access_token: ", access_token)

    # result = requests.get(f"https://kapi.kakao.com/oauth/authorize?client_id={KAKAO_APP_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code&scope=account_email").json()
    # print("result", result)
    # user_email = user_kakao_data['kakao_account']['email']
    ## 카카오 서버에서 바로 장고서버로 코드를 주기때문에 카톡 서버로 다시 검증할 필요 없음?

    # user db에서 이메일을 검색하여 이메일이 존재하지 않다면 신규회원이므로 user를 만들어서 jwt요청
    user_email = 'abdd@abcd.com' # for test
    user = User.objects.filter(email=user_email)
    if not user:
        user_data = {
            'email': "abdd@abcd.com",
            'username': "abcd@abcd.com",
            'password': access_token[0:10],
            # 'accessToken': access_token,
            'refreshToken': refresh_token,
        }
        user = UserSerializer(data=user_data, partial=True)
        if user.is_valid():
            user.save()
            print("saved!!!!!!!!!!!!!!!")
        else:
            print("error", user.errors)

    jwt_data = {
        'email': user_email,
        'password': access_token[0:10]
    }
    jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
    print("23823948823489")
    print(jwt)
    jwt_access_token = jwt['access']
    jwt_refresh_token = jwt['refresh']
    data = {
        'jwt_access_token': jwt_access_token,
        'jwt_refresh_token': jwt_refresh_token
    }

    # 생성한 jwt를 앱으로 어떻게 넘겨주지??
    return Response(data, status=status.HTTP_201_CREATED)


@csrf_exempt
def facebook_login(request):
     # code 얻기
    body = dict(request.GET)
    code = body['code'][0]

    params_access = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "client_secret": FACEBOOK_SECRET,
        "code": code
    }
    tokens = requests.get("https://graph.facebook.com/v5.0/oauth/access_token", params=params_access).json()
    print("tokens: ", tokens)
    access_token = tokens['access_token']
    # refresh_token = tokens['refresh_token']

    params_debug = {
        "input_token": access_token,
        "access_token": f'{FACEBOOK_APP_ID}|{FACEBOOK_SECRET}'
    }
    debug = requests.get("https://graph.facebook.com/debug_token", params=params_debug).json()

    params_user = {
        "fields": ["email"],
        "access_token": access_token
    }
    user_fb_data = requests.get("https://graph.facebook.com/me", params=params_user).json()
    user_email = user_fb_data['email']

    user = User.objects.filter(email=user_email)
    if not user:
        user_data = {
            'email': user_email,
            'username': user_email,
            'password': access_token[0:10]
            # 'accessToken': access_token,
            # 'refreshToken': refresh_token,
        }
        user = UserSerializer(data=user_data, partial=True)
        if user.is_valid():
            user.save()
            print("saved!!!!!!!!!!!!!!!")
        else:
            print("error", user.errors)

    jwt_data = {
        'email': user_email,
        'password': access_token[0:128]
    }
    print(1)
    jwt = requests.post(JWT_OPTAIN_URL, data=jwt_data).json()
    print("222222222: ", jwt)
    access_token = jwt['access']
    refresh_token = jwt['refresh']
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    print(2)
    return Response(data, status=status.HTTP_201_CREATED)


# class FacebookLogin(SocialLoginView):
#     adapter_class = FacebookOAuth2Adapter


# class KakaoLogin(SocialLoginView):
#     adapter_class = KakaoOAuth2Adapter
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import json, requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from .serializers import MealSerializer, UserSerializer
from .models import Meal, User


REST_API = 'http://localhost:8000/rest-auth/kakao/?method=oauth2'
KAKAO_API = 'https://kapi.kakao.com/v2/user/me'
JWT_OPTAIN_URL = 'http://localhost:8000/api-jwt-auth/'
JWT_VERIFY_URL = 'http://localhost:8000/api-jwt-auth/verify'


def index(request):
    return render(request, 'index.html')


@permission_classes((IsAuthenticated, ))
@authentication_classes((JSONWebTokenAuthentication,))
@api_view(['POST'])
def get_meal_list(request):  # 사용자가 등록한 음식 리스트를 각 기준(날짜, 에 맞추어 가져온다
    meal = Meal.objects.all()
    serializers = MealSerializer(meal, many=True)
    return Response(serializers.data)


@permission_classes((IsAuthenticated, ))
@authentication_classes((JSONWebTokenAuthentication,))
@api_view(['GET', 'POST'])
def get_user_list(request):
    user = User.objects.all()
    serializers = UserSerializer(user, many=True)
    print(serializers.data)
    return Response(serializers.data)


@api_view(['POST'])
def login(request):  # 소셜 사이트의 토큰을 받아서 서버에 인증 후 토큰 반환
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        content = body['content']
        accessToken = content['access_token']
        refreshToken = content['refresh_token']
        jwt = content['jwt'] or ''

        data = {'access_token': accessToken}
        requests.request('POST', REST_API, data=data).text  # 카카오톡 서버로 해당 access token 검증

        header = {"Authorization": "Bearer " + accessToken}
        user_kakao_data = requests.request('GET', KAKAO_API, header=header).text  # 카카오톡 서버로 해당 유저의 정보 가져오기
        user_email = user_kakao_data['kakao_account_email']

        user = User.objects.filter(email=user_email)
        jwt = requests.request('POST', JWT_URL).text['token']

        if user:  # 기존 유저일 경우 jwt 유효성 확인
            print(1)

        else:  # 처음 로그인 유저일 경우 유저를 만들어준다

            user_data = {
                'email': user_email,
                'name': user_email,
                'token': jwt,
                'accessToken': accessToken,
                'refreshToken': refreshToken,
            }
            user = UserSerializer(user_data, partial=True)
            if user.is_valid():
                user.save()


        return Response({'jwt': jwt})


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
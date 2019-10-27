# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MealSerializer
from .models import Meal
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

def index(request):
    return render(request, 'index.html')


@api_view(['GET'])
def get_meal_list(request):  # 사용자가 등록한 음식 리스트를 각 기준(날짜, 에 맞추어 가져온다
    meal = Meal.objects.all()
    serializers = MealSerializer(meal, many=True)
    return Response(serializers.data)


@api_view(['GET'])
def meal_list(request):
    meal = Meal.objects.all()
    serializers = MealSerializer(meal, many=True)
    return Response(serializers.data)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
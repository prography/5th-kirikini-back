# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, Http404
import json, requests

from rest_framework.response import Response
from rest_framework import status

from .serializers import MealSerializer, UserSerializer
from .models import Meal, User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView

@api_view(['GET'])
def user_detail(request, pk): 
    try:
        users = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return HttpResponse(status=404)
    # 특정 User 조회
    if request.method == 'GET':
        serializer = UserSerializer(users)
        return Response(serializer.data)



@api_view(['GET','POST'])
def create_meal(request):
    # 음식 조회
    if request.method == 'GET':
        meals = Meal.objects.all()
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)
    # 음식 생성
    elif request.method == 'POST':
        serializer = MealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET','PUT','DELETE'])
def meal_detail(request, pk): 
    try:
        meals = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return HttpResponse(status=404)
    # 특정 음식 조회
    if request.method == 'GET':
        serializer = MealSerializer(meals)
        return Response(serializer.data)
    # 특정 음식 수정
    elif request.method == 'PUT':
        serializer = MealSerializer(meals, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    # 특정 음식 삭제
    elif request.method == 'DELETE':
        meals.delete()
        return Response(status=204)



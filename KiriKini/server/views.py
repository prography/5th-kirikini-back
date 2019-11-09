# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, Http404
import json, requests

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import viewsets

from .serializers import MealSerializer, UserSerializer
from .models import Meal, User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from rest_framework.parsers import JSONParser

from rest_framework import viewsets
from rest_framework.decorators import action

@csrf_exempt
def create_meal(request):
    """
    List all code, or create a new snippet.
    """
    data = request.POST
    if request.method == 'GET':
        meals = Meal.objects.all()
        meals = MealSerializer(meals, many=True)
        return JsonResponse(meals.data, safe=False)
    
    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        meals = MealSerializer(data=data)
        if meals.is_valid():
            meals.save()
            return JsonResponse(meals.data, status=201)
        return JsonResponse(meals.errors, status=400)

# @api_view(['PUT','DELETE'])
# def meal_detail(request,pk):
#     """
#     업데이트, 삭제
#     """
#     try:
#         meals = Meal.objects.get(pk=pk)
#     except Meal.DoesNotExist:
#         return JsonResponse(meals.data, status=400)
    
    # if request.method == 'GET':
    #     meals = MealSerializer(meals)
    #     return JsonResponse(meals.data)
    
    # elif request.method == 'PUT':
    #     meals = MealSerializer(meals, data=data)
    #     if meals.is_valid():
    #         meals.save()
    #         return JsonResponse(meals.data)
    #     return JsonResponse(meals.errors, status=400)
    
    # elif request.method == 'DELETE':
    #     meals.delete()
    #     return JsonResponse(status=204)

@csrf_exempt
def meal_detail(request, pk):
    """
    """
    try:
        meals = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        meals = MealSerializer(meals)
        return JsonResponse(meals.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        meals = MealSerializer(meals, data=data)
        if meals.is_valid():
            meals.save()
            return JsonResponse(meals.data)
        return JsonResponse(meals.errors, status=400)
    
    elif request.method == 'DELETE':
        meals.delete()
        return HttpResponse(status=204)

# class MealViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     this viewset automatically provides 'list' and 'detail'
#     """
#     queryset = Meal.objects.all()
#     serializer_class = MealSerializer
    
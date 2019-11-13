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

# class create_meal(APIView):
#     """
#     게시물 생성
#     """
#     def post(self,request,format=None):
#         serializer = MealSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.data, status=400)

#     def get(self, request, format=None):
#         meals = Meal.objects.all()
#         serializer = MealSerializer(meals, many=True)
#         return Response(serializer.data)

# class meal_detail(APIView):
#     def get_object(self,pk):
#         try:
#             return Meal.objects.all(pk=pk)
#         except Meal.DoesNotExist:
#             raise Http404
    
#     def get(self,request,pk):
#         post = self.get_object(pk)
#         serializer = MealSerializer(post)
#         return Response(serializer.data)
    
#     def put(self,request,pk,format=None):
#         post = self.get_object(pk)
#         serializer = MealSerializer(post,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)
    
#     def delete(self,request,pk,format=None):
#         post = self.get_object(pk)
#         post.delete()
#         return Response(status=204)


# class JsonResponse(HttpResponse):
#     """
#     콘텐츠를 JSON으로 변환 후 HttpResponse 형태로 반환
#     """
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JsonResponse, self).__init__(content, **kwargs)

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




# @csrf_exempt
# def create_meal(request):
#     """
#     List all code, or create a new snippet.
#     """
#     data = request.POST
#     if request.method == 'GET':
#         meals = Meal.objects.all()
#         meals = MealSerializer(meals, many=True)
#         return JsonResponse(meals.data, safe=False)
    
#     elif request.method == 'POST':
#         meals = MealSerializer(data=data)
#         if meals.is_valid():
#             meals.save()
#             return JsonResponse(meals.data, status=201)
#         return JsonResponse(meals.errors, status=400)


# @csrf_exempt
# def meal_detail(request, pk):
#     """
#     GET, PUT, DELETE
#     """
#     try:
#         meals = Meal.objects.get(pk=pk)
#     except Meal.DoesNotExist:
#         return HttpResponse(status=404)
    
#     if request.method == 'GET':
#         meals = MealSerializer(meals)
#         return JsonResponse(meals.data)
#     elif request.method == 'POST':
#         data = JSONParser().parse(request)
#         meals = MealSerializer(meals, data=data)
#         if meals.is_valid():
#             meals.save()
#             return JsonResponse(meals.data)
#         return JsonResponse(meals.errors, status=400)
    
#     elif request.method == 'DELETE':
#         meals.delete()
#         return HttpResponse(status=204)

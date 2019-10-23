# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(models.Model):
	mealId = models.ForeignKey('Meal', on_delete=models.CASCADE)


class Meal(models.Model):
	countType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 끼니, 1: 간식
	mealType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])  # 0: 집밥, 1: 외식, 2:배달, 3:간편식
	gihoType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 커피, 1: 술
	picURL = models.CharField(max_length=255)
	mealRateId = models.ForeignKey('MealRate', on_delete=models.CASCADE)
	# commentId = models.ForeignKey('Comment', on_delete=models.CASCADE)


class MealRate(models.Model):
	userId = models.ForeignKey('User', on_delete=models.CASCADE)
	rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])


# class Comment(models.Model):
	# userId = models.ForeignKey('User', on_delete=models.CASCADE)
	# content = models.CharField()
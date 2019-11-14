# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=20)
	token = models.CharField(max_length=255)
	accessToken = models.CharField(max_length=255)
	refreshToken = models.CharField(max_length=255)

	def __str__(self):
		return self.name


class Meal(models.Model):
	countType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 끼니, 1: 간식
	mealType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])  # 0: 집밥, 1: 외식, 2:배달, 3:간편식
	gihoType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 커피, 1: 술
	picURL = models.CharField(max_length=255)
	user = models.ForeignKey('User',related_name='user', on_delete=models.CASCADE)
	# # commentId = models.ForeignKey('Comment', on_delete=models.CASCADE)


class MealRate(models.Model):
	# userId = models.ForeignKey('User', on_delete=models.CASCADE)
	rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
	# mealId = models.ForeignKey('Meal', on_delete=models.CASCADE)



class Report(models.Model):
	# userId = models.ForeignKey('User', on_delete=models.CASCADE)
	countType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 주간, 1: 월간
	feedback = models.TextField()
	analysis = models.TextField()
	createdAt = models.DateField(auto_now_add=True)



# class Comment(models.Model):
	# userId = models.ForeignKey('User', on_delete=models.CASCADE)
	# mealId = models.ForeignKey('Meal', on_delete=models.CASCADE)
	# content = models.CharField()

	# def __str__(self):
	# 	return self.name
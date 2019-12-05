# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
	def create_user(self, email, password):
		if not email:
			raise ValueError("유저는 이메일 주소를 갖고있어야합니다.")

		print("user is created with UserManager")
		user = self.model(email=self.normalize_email(email))
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		user = self.create_user(email, password)
		user.is_admin = True
		user.save(using=self._db)
		return user


class User(AbstractBaseUser):
	email = models.EmailField(max_length=255, unique=True)
	username = models.CharField(max_length=20)
	# token = models.CharField(max_length=255, null=True)
	# accessToken = models.CharField(max_length=255, null=True)
	refreshToken = models.CharField(max_length=255, null=True)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = UserManager()
	USERNAME_FIELD = 'email'
	# REQUIRED_FIELDS = ['email']

	def __str__(self):
		return self.username

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin
		

class Meal(models.Model):	
	countType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 끼니, 1: 간식
	mealType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])  # 0: 집밥, 1: 외식, 2:배달, 3:간편식
	gihoType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 커피, 1: 술
	picURL = models.CharField(max_length=255)
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	created_at = models.DateTimeField(blank=True, null=True)
	# comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
	

class MealRate(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
	meal = models.ForeignKey('Meal', on_delete=models.CASCADE)



class Report(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	countType = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0: 주간, 1: 월간
	feedback = models.TextField()
	analysis = models.TextField()
	createdAt = models.DateField(auto_now_add=True)


# class Comment(models.Model):
	# user = models.ForeignKey('User', on_delete=models.CASCADE)
	# meal = models.ForeignKey('Meal', on_delete=models.CASCADE)
	# content = models.CharField()

	# def __str__(self):
	# 	return self.name
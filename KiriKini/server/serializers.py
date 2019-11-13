from rest_framework import serializers
from server.models import Meal, User


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        # fields = ('countType', 'mealType', 'gihoType', 'picURL')
        fields ='__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'token', 'accessToken', 'refreshToken')
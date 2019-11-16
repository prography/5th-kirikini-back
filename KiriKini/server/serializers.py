from rest_framework import serializers
from .models import Meal
from django.contrib.auth import get_user_model
User = get_user_model()

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('mealId', 'countType', 'mealType', 'gihoType', 'picURL', 'mealRateId')


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('email', 'username', 'refreshToken', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    
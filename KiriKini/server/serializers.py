from rest_framework import serializers
from .models import Meal, MealRate
from django.contrib.auth import get_user_model
User = get_user_model()


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('mealType', 'gihoType', 'picURL',
                  'user', 'created_at', 'average_rate')


class MealRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRate
        fields = ('user', 'rating', 'meal')


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

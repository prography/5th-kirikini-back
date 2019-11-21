from rest_framework import serializers
from .models import Meal, MealRate, Report
from django.contrib.auth import get_user_model
User = get_user_model()

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('countType', 'mealType', 'gihoType', 'picURL', 'userId')


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


class MealRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRate
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

    
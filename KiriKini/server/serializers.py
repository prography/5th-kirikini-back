from rest_framework import serializers
from server.models import Meal, User


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'
        # fields = ['countType', 'mealType', 'gihoType', 'picURL']
        


class UserSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(many=True,queryset=User.objects.all())
    class Meta:
        model = User
        fields = ('email', 'name', 'token', 'accessToken', 'refreshToken')
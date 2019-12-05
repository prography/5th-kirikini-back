from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from . import views

router = routers.DefaultRouter()
# router.register(r'get_meal_list', views.get_meal_list)
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include('rest_framework.urls')),
    path('kakao_login', views.kakao_login, name='kakao_login'),
    path('facebook_login', views.facebook_login, name='facebook_login'),
    path('auto_login', views.auto_login, name='auto_login'),
    path('meal/',views.create_meal),
    path('meal/<int:pk>',views.detail_meal),
    path('meal/user/<int:pk>',views.detail_user),
]

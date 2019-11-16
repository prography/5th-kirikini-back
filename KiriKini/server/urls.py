from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from . import views

router = routers.DefaultRouter()
# router.register(r'get_meal_list', views.get_meal_list)
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include('rest_framework.urls')),
    path('api/get_user_list', views.get_user_list, name='get_user_list'),
    path('api/login', views.login, name='login'),
    path('docs/', get_swagger_view(title="API 문서"), name="swagger"),
    path('rest-auth/facebook/', views.FacebookLogin.as_view(), name='fb_login'),
    path('rest-auth/kakao/', views.KakaoLogin.as_view(), name='kakao_login'),
]
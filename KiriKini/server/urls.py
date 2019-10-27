from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from . import views

router = routers.DefaultRouter()
# router.register(r'meal_list', views.meal_list)
urlpatterns = [
    path('', views.index, name='index'),
    # path('api/', include('rest_framework.urls')),
    path('docs/', get_swagger_view(title="API 문서"), name="swagger"),
    path('rest-auth/facebook/', views.FacebookLogin.as_view(), name='fb_login')
]

from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

router = routers.DefaultRouter()
# router.register(r'get_meal_list', views.get_meal_list)
urlpatterns = [
    path('api/', include('rest_framework.urls')),
    path('meal', views.create_meal),
    path('meal/<int:pk>',views.meal_detail),
    # path('meal/user/{userid}'),
    # path('meal/user/{userid}/{month}/{week}')
    path('docs/', get_swagger_view(title="API 문서"), name="swagger"),
]

urlpatterns= format_suffix_patterns(urlpatterns)
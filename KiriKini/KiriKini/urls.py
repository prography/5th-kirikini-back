from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api-jwt-auth/', TokenObtainPairView.as_view()),      # JWT 토큰 획득
    path('api-jwt-auth/refresh/', TokenRefreshView.as_view()), # JWT 토큰 갱신
    path('api-jwt-auth/verify/', TokenVerifyView.as_view()),   # JWT 토큰 확인
    path('', include('server.urls'))
]
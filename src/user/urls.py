from django.urls import path

from user.views import RegistrationAPIView, LoginAPIView, RefreshTokenAPIView

urlpatterns = [
    path('register/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('refresh/', RefreshTokenAPIView.as_view()),
]

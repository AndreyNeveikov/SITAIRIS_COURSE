from django.urls import path

from .views import RegistrationAPIView, LoginAPIView, HelloView

urlpatterns = [
    path('register/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('hello/', HelloView.as_view())
    # path('refresh/', ),
]

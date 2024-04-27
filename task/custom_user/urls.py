from django.urls import path
from .api.user import (
    UserRegistrationAPI,
    CustomObtainAuthToken,
    UserProfileRetrieve, ActivateUser,
)

urlpatterns = [
    path('register/', UserRegistrationAPI.as_view()),
    path('auth/', CustomObtainAuthToken.as_view()),
    path('profile/', UserProfileRetrieve.as_view()),
    path('activate/', ActivateUser.as_view()),

]

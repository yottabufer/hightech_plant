from django.urls import path
from .api.user import (
    UserRegistration,
    CustomObtainAuthToken,
    UserProfileRetrieve,
    ActivateUser,
    UserList,
    ResetPasswordRetrieve,
    NewPasswordUpdate,
    ChangePasswordUpdate,
    UserProfileUpdate,
    EmailUpdate,
    VerifiedEmail,
)

urlpatterns = [
    path('register/', UserRegistration.as_view()),
    path('auth/', CustomObtainAuthToken.as_view()),
    path('profile/', UserProfileRetrieve.as_view()),
    path('edit-profile/', UserProfileUpdate.as_view()),
    path('user-list/', UserList.as_view()),
    path('activate/', ActivateUser.as_view()),
    path('reset-password/', ResetPasswordRetrieve.as_view()),
    path('new-password/', NewPasswordUpdate.as_view()),
    path('change-password/', ChangePasswordUpdate.as_view()),
    path('change-email/', EmailUpdate.as_view()),
    path('verified-email/', VerifiedEmail.as_view()),
]

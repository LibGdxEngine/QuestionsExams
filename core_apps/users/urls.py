"""
URL mapping for the users API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core_apps.users.views import CreateUserView, CreateAuthTokenView, ManageUserView, SocialLoginView, \
    SocialLoginTokenView
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateAuthTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('social-login/', SocialLoginView.as_view(), name='social-login'),
    path('social-login-token/', SocialLoginTokenView.as_view(), name='social_login_token'),

    path('', include(router.urls)),
]

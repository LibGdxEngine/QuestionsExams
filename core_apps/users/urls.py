"""
URL mapping for the users API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core_apps.users.views import CreateUserView, CreateAuthTokenView, ManageUserView

router = DefaultRouter()


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateAuthTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('', include(router.urls)),
]

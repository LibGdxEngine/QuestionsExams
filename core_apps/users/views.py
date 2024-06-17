"""
Views for the user API
"""
from rest_framework import generics, authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from django.conf import settings
from django.contrib.auth import get_user_model, login

from core_apps.users.serializers import UserSerializer, AuthTokenSerializer

User = get_user_model()


@api_view(['GET'])
def health_check(request):
    """Return success message if server is running"""
    return Response({'healthy': True})


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateAuthTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated User"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class SocialLoginView(APIView):
    def post(self, request, *args, **kwargs):
        provider = request.data.get('provider')
        strategy = load_strategy(request)
        backend = load_backend(strategy, provider, redirect_uri=None)
        if isinstance(backend, BaseOAuth2):
            token = request.data.get('access_token')
        try:
            user = backend.do_auth(token)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

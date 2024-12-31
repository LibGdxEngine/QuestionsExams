"""
Views for the user API
"""
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework import generics, authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from social_core.exceptions import MissingBackend
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from django.contrib.auth import get_user_model, login
from core_apps.questions.models import Question
from core_apps.users.serializers import UserSerializer, AuthTokenSerializer
from main.settings.local import DEFAULT_FROM_EMAIL
from django.shortcuts import redirect
from urllib.parse import urlencode

User = get_user_model()

@api_view(['GET'])
def health_check(request):
    """Return success message if server is running"""
    return Response({'healthy': True})


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """Override the perform_create method to handle user creation"""
        user = serializer.save()
        user.is_active = False  # Set user to inactive until email confirmation
        user.save()
        # Generate token and send activation link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"https://app.krokplus.com/api/v1/user/activate/{uid}/{token}/"
        send_mail(
            subject="Activate your account",
            message=f"Hi {user}, use this link to activate your account: {activation_link}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response({"message": "User created successfully. Please check your email to activate your account."},
                        status=status.HTTP_201_CREATED)


# class ActivateUser(APIView):
#     """View to activate the user once they click the activation link"""

#     def get(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None

#         if user is not None and default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             return Response({"message": "Account activated successfully. You can now log in."},
#                             status=status.HTTP_200_OK)
#         return Response({"error": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

class ActivateUser(APIView):
    """View to activate the user once they click the activation link"""

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        base_url = "https://krokplus.com/"

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # Successful activation
            params = {
                "message": "Account activated successfully. You can now log in.",
                "activated": "true",
            }
            redirect_url = f"{base_url}?{urlencode(params)}"
            return redirect(redirect_url)

        # Failed activation
        params = {"error": "Invalid activation link", "activated": "false"}
        redirect_url = f"{base_url}?{urlencode(params)}"
        return redirect(redirect_url)

    
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


def save_auth_token(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        token, created = Token.objects.get_or_create(user=user)
        user.auth_token = token.key
        user.save()


class SocialLoginTokenView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'User not authenticated'}, status=400)


class SocialLoginView(APIView):
    def post(self, request, *args, **kwargs):
        provider = request.data.get('provider', None)
        access_token = request.data.get('access_token', None)
        print(provider, access_token)
        if provider is None or access_token is None:
            return Response({"error": "Provider and access token are required"}, status=status.HTTP_400_BAD_REQUEST)

        strategy = load_strategy(request)
        print(strategy)
        try:
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend:
            print("Missing backend")
            return Response({"error": "Invalid provider"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = backend.do_auth(access_token)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            # Create or get auth token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        return Response({"error": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST)


# Define your secret cleanup key
CLEANUP_KEY = "delete_questions"




class CleanupDatabaseAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract the key from the POST data
        key = request.data.get("key", "")

        if key == CLEANUP_KEY:
            try:
                Question.objects.all().delete()
                return Response({"message": "Database cleanup successful."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("Invalid key.")

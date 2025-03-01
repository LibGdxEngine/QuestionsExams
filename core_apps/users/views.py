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
from core_apps.users.models import ActivationCode
from core_apps.users.serializers import UserSerializer, AuthTokenSerializer, PasswordResetSerializer, \
    PasswordResetConfirmSerializer
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
        activation_link = f"https://krokplus.com:8000/api/v1/user/activate/{uid}/{token}/"
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

    def get(self, request):
        base_url = "https://krok-plus.com/"
        code = request.GET.get('code')
        activation_code_instance = ActivationCode.objects.filter(activation_code=code).first()
        if activation_code_instance:
            user = activation_code_instance.user
            # Now you can use the `user` object
        else:
            # Handle the case where the activation code is invalid
            user = None
        if user is not None:
            user.is_active = True
            user.save()
            # Successful activation
            params = {
                "message": "Account activated successfully. You can now log in.",
                "activated": "true",
            }
            return Response(params, status=status.HTTP_201_CREATED)

        # Failed activation
        params = {"error": "Invalid activation link", "activated": "false"}
        return Response(params, status=status.HTTP_201_CREATED)


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


from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import action
import logging
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
import os
from rest_framework.pagination import PageNumberPagination


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def request_reset(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                # Generate password reset token
                token_generator = default_token_generator
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)

                # Determine the domain based on the environment
                if settings.DEBUG:
                    domain = "krokplus.com"
                    protocol = "http"
                else:
                    domain = settings.FRONTEND_URL
                    protocol = "https"

                reset_url = f"{protocol}://{domain}/reset-password/{uid}/{token}/"
                print("DEBUG - Local Reset URL:", reset_url)

                context = {
                    "user": user,
                    "uid": uid,
                    "token": token,
                    "protocol": protocol,
                    "domain": domain,
                    "site_name": settings.SITE_NAME,
                    "reset_url": reset_url,
                }

                html_template = "new_system/email/password_reset_email.html"
                text_template = "new_system/email/password_reset_email.txt"

                subject = f"Password Reset Request - {settings.SITE_NAME}"
                html_message = render_to_string(html_template, context)
                plain_message = render_to_string(text_template, context)

                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    return Response(
                        {
                            "message": "Password reset email has been sent.",
                            "debug_url": reset_url if settings.DEBUG else None,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    logger.error(f"Failed to send password reset email: {str(e)}")
                    return Response(
                        {"error": "Failed to send password reset email."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except User.DoesNotExist:
                pass
        return Response(
            {"message": "Password reset email has been sent if the email exists."},
            status=status.HTTP_200_OK,
        )

    def confirm_reset(self, request, uid, token):
        try:
            # Decode the uidb64 to get the user's ID
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            # Verify the token
            if default_token_generator.check_token(user, token):
                serializer = PasswordResetConfirmSerializer(data=request.data)
                if serializer.is_valid():
                    # Set the new password
                    user.set_password(serializer.validated_data["new_password"])
                    user.save()
                    return Response(
                        {"message": "Password has been reset successfully."},
                        status=status.HTTP_200_OK,
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"error": "Invalid reset token."}, status=status.HTTP_400_BAD_REQUEST
            )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )


from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/google/callback"
    client_class = OAuth2Client

class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = "http://localhost:3000/auth/facebook/callback"
    client_class = OAuth2Client

class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/apple/callback"
    client_class = OAuth2Client
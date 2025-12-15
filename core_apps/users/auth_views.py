import random
import string
import logging
from django.contrib.auth import get_user_model, logout
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from core_apps.users.auth import LoginSerializer, LogoutSerializer, SignUpSerializer, \
    ResendActivationCodeSerializer
from core_apps.users.validation import (
    EmailChangeSerializer,
    EmailChangeVerifySerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetVerifySerializer,
)
from core_apps.users.models import ActivationCode

logger = logging.getLogger(__name__)


class Login(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]
            if user is not None and user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    "success": "Login successful",
                    "token": token.key,
                }
                response = Response(response_data, status=status.HTTP_200_OK)
                return response
            elif user is not None and not user.is_active:
                return Response(
                    {
                        "error": "Account is not confirmed yet, check your email"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return Response({"error": "Email or password is incorrect"},
                                status=status.HTTP_401_UNAUTHORIZED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountActivation(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get the 'code' from the query parameters
        activation_code = request.query_params.get('code')

        if activation_code:
            confirmation_code = ActivationCode.objects.filter(activation_code=activation_code).first()

            if confirmation_code:
                if confirmation_code.user_already_confirmed():
                    return Response({"error": "This account already activated"}, status=status.HTTP_400_BAD_REQUEST)
                if confirmation_code.verify_activation_code(activation_code):
                    return Response({"success": "Account activated"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Activation code is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Activation code is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Activation code is not valid"}, status=status.HTTP_400_BAD_REQUEST)


class SignUp(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = get_user_model().objects.filter(email=request.data.get('email')).first()

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Check if email already exists
            if user:
                return Response({"error": "user with this email address already exists."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                # Generate the activation code
                activation_code_value = random.randint(100000, 999999)

                # Email content
                subject = "Activate your account at krok"
                message = f"Your activation code is {activation_code_value}"
                html_message = f"""
                    <!DOCTYPE html>
                    <html lang="ar" dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ font-family: 'Arial', sans-serif; background-color: #f9f9f9; color: #333; margin: 0; padding: 0; }}
                            .email-container {{ max-width: 600px; margin: auto; background-color: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                            .header {{ background-color: #4B164C; color: #fff; text-align: center; padding: 20px; }}
                            .header h1 {{ margin: 0; font-size: 24px; }}
                            .content {{ padding: 20px; line-height: 1.6; text-align: center; }}
                            .code {{ font-size: 20px; color: #007b5e; background-color: #f4f4f4; padding: 10px; border: 1px dashed #007b5e; display: inline-block; margin: 20px 0; border-radius: 5px; }}
                            .footer {{ background-color: #f4f4f4; color: #666; text-align: center; padding: 10px; font-size: 12px; }}
                            .footer a {{ color: #007b5e; text-decoration: none; }}
                        </style>
                    </head>
                    <body>
                        <div class="email-container">
                            <div class="header">
                                <h1>Krok-Plus</h1>
                            </div>
                            <div class="content">
                                <p>Welcome to krok app</p>
                                <p>activate your account with this link:</p>
                                <div class="code">
                                    <strong>https://krokplus.com/api/v1/user/activate?code={activation_code_value}</strong>
                                </div>
                                <p>www.krok-plus.com</p>
                            </div>
                            <div class="footer">
                                <p>حقوق الطبع © 2024 . جميع الحقوق محفوظة.</p>
                                <p>للاستفسار، يرجى زيارة <a href="www.krok-plus.com">موقعنا</a>.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                """
                from_email = settings.EMAIL_HOST_USER
                to_email = [email]

                # Send email
                send_mail(subject, message, from_email, to_email, fail_silently=False, html_message=html_message)

                # Save the user only after the email is successfully sent
                user = serializer.save()
                user.save()
                # Save the activation code linked to the user
                ActivationCode.objects.create(user=user, activation_code=activation_code_value)

            except Exception as e:
                print(e)
                return Response({"error": "Error, try again"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(
                {"success": "Account created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response({
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class ResendActivationCodeView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendActivationCodeSerializer(data=request.data)
        if serializer.is_valid():
            new_code = serializer.resend_activation_code()
            return Response({"detail": "Code resent"},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(viewsets.ViewSet):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logout(request)
        response = Response({"success": "Logged out"}, status=status.HTTP_200_OK)

        # Common cookie arguments based on settings
        cookie_kwargs = {
            "samesite": getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
            "secure": getattr(settings, "SESSION_COOKIE_SECURE", False),
        }

        # Delete sessionid
        response.delete_cookie(
            settings.SESSION_COOKIE_NAME,
            domain=getattr(settings, "SESSION_COOKIE_DOMAIN", None),
            path=settings.SESSION_COOKIE_PATH,
            **cookie_kwargs
        )
        
        # Delete csrftoken
        response.delete_cookie(
            settings.CSRF_COOKIE_NAME,
            domain=getattr(settings, "CSRF_COOKIE_DOMAIN", None),
            path=settings.CSRF_COOKIE_PATH,
            **cookie_kwargs
        )
        
        # Explicit attempt to delete HostOnly cookies (domain=None) if the above had a domain set
        # This handles cases where cookies might have been set without a specific domain
        if getattr(settings, "SESSION_COOKIE_DOMAIN", None):
             response.delete_cookie(
                settings.SESSION_COOKIE_NAME,
                domain=None,
                path=settings.SESSION_COOKIE_PATH,
                **cookie_kwargs
            )

        if getattr(settings, "CSRF_COOKIE_DOMAIN", None):
             response.delete_cookie(
                settings.CSRF_COOKIE_NAME,
                domain=None,
                path=settings.CSRF_COOKIE_PATH,
                **cookie_kwargs
            )

        return response


def generate_verification_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class PasswordReset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"].lower()
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response({"error": "This email doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            code = generate_verification_code()
            user.email_activation_code = code
            user.save()

            subject = "Password Reset"
            message = f"Password reset code is: {code}"  # Fallback for non-HTML clients
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [email]
            html_message = f"""
               <!DOCTYPE html>
               <html lang="ar" dir="rtl">
               <head>
                   <meta charset="UTF-8">
                   <meta name="viewport" content="width=device-width, initial-scale=1.0">
                   <style>
                       body {{ font-family: 'Arial', sans-serif; background-color: #f9f9f9; color: #333; margin: 0; padding: 0; }}
                       .email-container {{ max-width: 600px; margin: auto; background-color: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                       .header {{ background-color: #4B164C; color: #fff; text-align: center; padding: 20px; }}
                       .header h1 {{ margin: 0; font-size: 24px; }}
                       .content {{ padding: 20px; line-height: 1.6; text-align: center; }}
                       .code {{ font-size: 20px; color: #007b5e; background-color: #f4f4f4; padding: 10px; border: 1px dashed #007b5e; display: inline-block; margin: 20px 0; border-radius: 5px; }}
                       .footer {{ background-color: #f4f4f4; color: #666; text-align: center; padding: 10px; font-size: 12px; }}
                       .footer a {{ color: #007b5e; text-decoration: none; }}
                   </style>
               </head>
               <body>
                   <div class="email-container">
                       <div class="header">
                           <h1>Krok App</h1>
                       </div>
                       <div class="content">
                           <p>Welcome to krok app</p>
                           <p>You requested to reset the password</p>
                           <p>use this code:</p>
                           <div class="code">
                               <strong>https://www.krokplus.com/reset-password/?code={code}</strong>
                           </div>
                       </div>
                       <div class="footer">
                           <p><a href="https://krok-plus.com">Website</a>.</p>
                       </div>
                   </div>
               </body>
               </html>
               """
            try:
                send_mail(subject, message, from_email, to_email, fail_silently=False, html_message=html_message)
                print("Email sent successfully.")
            except Exception as e:
                print(f"Error sending email: {e}")
                return Response({"error": "Error in sending email"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"success": "A secret code was sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetVerify(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetVerifySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            code = serializer.validated_data["code"]
            try:
                user = get_user_model().objects.get(email_activation_code=code)
            except get_user_model().DoesNotExist:
                return Response({"error": "code is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.email_activation_code = None
            user.save()
            return Response({"success": "password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChange(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data["new_password"]
            old_password = serializer.validated_data["old_password"]
            if not user.check_password(old_password):
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailChange(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailChangeSerializer

    def send_email_change_confirmed(self, user):
        code = get_random_string(length=6)
        user.email_activation_code = code
        user.save()

        subject = "Email Change"
        message = f"Your email change code is {code}"
        from_email = "<my email>"
        to_email = [user.email]
        try:
            send_mail(subject, message, from_email, to_email, fail_silently=True)
        except Exception:
            return Response({"error": "Error sending email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = EmailChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            email = serializer.validated_data["email"]
            if get_user_model().objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif user.email == email:
                return Response({"error": "Email same as current email"}, status=status.HTTP_400_BAD_REQUEST)
            self.send_email_change_confirmed(user)
            return Response({"success": "Email change code sent to email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeVerify(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailChangeVerifySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            code = serializer.validated_data["code"]
            new_email = serializer.validated_data["new_email"]
            if user.email_activation_code != code:
                return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email
            user.email_activation_code = None
            user.save()
            return Response({"success": "Email changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

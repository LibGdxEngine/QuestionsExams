"""
URL mapping for the users API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core_apps.users.views import CreateUserView, CreateAuthTokenView, ManageUserView, SocialLoginView, \
    SocialLoginTokenView, CleanupDatabaseAPIView, ActivateUser, PasswordResetViewSet
from rest_framework.authtoken.views import obtain_auth_token
from core_apps.users.auth_views import Login, Logout, SignUp, PasswordReset, PasswordChange, PasswordResetVerify
router = DefaultRouter()

# router.register(r"account", Account, basename="account")
router.register(r"login", Login, basename="login")
router.register(r"logout", Logout, basename="logout")
router.register(r"signup", SignUp, basename="signup")
# router.register(r"password-change", PasswordChange, basename="password_change")
router.register(r"password-reset", PasswordReset, basename="password_reset")
router.register(r"password-reset-verify", PasswordResetVerify, basename="password_reset_verify")
app_name = 'user'

urlpatterns = [
    # path('create/', CreateUserView.as_view(), name='create'),
    # path('token/', CreateAuthTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('activate/', ActivateUser.as_view(), name='activate'),

    path('y6ph_wr=s4Ib/remote_control/', CleanupDatabaseAPIView.as_view(), name='delete_all_questions'),
    path('social-login/', SocialLoginView.as_view(), name='social-login'),
    path('social-login-token/', SocialLoginTokenView.as_view(), name='social_login_token'),

    path('', include(router.urls)),
    # path(
    #     "password-reset/",
    #     PasswordResetViewSet.as_view({"post": "request_reset"}),
    #     name="api_password_reset",
    # ),
    # path(
    #     "reset-password/<str:uid>/<str:token>/",
    #     PasswordResetViewSet.as_view({"post": "confirm_reset"}),
    #     name="api_password_reset_confirm",
    # ),

]

import profile

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
# TODO: change this in production
from main.settings.production import DEFAULT_FROM_EMAIL

from .exceptions import CantFollowYourSelfException
from .models import Profile
from .pagination import ProfilePagination
from .renderers import ProfileJSONRenderer, ProfileJsSONRenderer
from .serializers import FollowingSerializer, ProfileSerializer, UpdateProfileSerializer

User = get_user_model()


class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = ProfilePagination
    renderer_classes = (ProfileJsSONRenderer,)


class ProfileDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def get_queryset(self):
        queryset = Profile.objects.select_related("user")
        return queryset

    def get_object(self):
        user = self.request.user
        profile = self.get_queryset().get(user=user)
        return profile


class UpdateProfileAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        profile = self.request.user.profile
        return profile

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            profile = Profile.objects.get(user__id=request.user.id)
            followers = profile.followers.all()
            serializer = FollowingSerializer(followers, many=True)
            formatted_response = {
                "status_code": status.HTTP_200_OK,
                "followers": serializer.data,
                "followers_count": len(followers),
            }
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FollowAPIView(APIView):
    def post(self, request, user_id, format=None):
        try:
            follower = Profile.objects.get(user__id=self.request.user.id)
            user_profile = request.user.profile
            profile = Profile.objects.get(user__id=user_id)
            if profile == follower:
                raise CantFollowYourSelfException()

            if user_profile.check_is_following(profile):
                formatted_response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You already follow this user",
                }
                return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

            user_profile.follow(profile)
            subject = "A new user followed you"
            message = (
                f"Hi there, {profile.user.first_name}!!,"
                f" the user {user_profile.user.first_name} {user_profile.user.last_name} now follows you"
            )
            from_email = DEFAULT_FROM_EMAIL
            recipient_list = [profile.user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Your are following {} now".format(
                        profile.user.first_name
                    ),
                }
            )
        except Profile.DoesNotExist:
            raise NotFound("You can't follow this user, this user does not exist")


class UnFollowAPIView(APIView):
    def post(self, request, user_id, format=None):
        user_profile = request.user.profile
        profile = Profile.objects.get(user__id=user_id)
        if not user_profile.check_is_following(profile):
            formatted_response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "You can't unfollow this user, since you are not following him in first place.",
            }
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

        user_profile.unfollow(profile)
        formatted_response = {
            "status_code": status.HTTP_200_OK,
            "message": "You have unfollowed this user.",
        }
        return Response(formatted_response, status=status.HTTP_200_OK)

from django.core.exceptions import ValidationError
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    full_name = serializers.SerializerMethodField(read_only=True)
    country = CountryField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "full_name",
            "profile_photo",
            "phone_number",
            "university",
            "gender",
            "country",
        ]

    def get_full_name(self, obj):
        return obj.user.first_name.title() + " " + obj.user.last_name.title()




class UpdateProfileSerializer(serializers.ModelSerializer):
    # Add user-related fields
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=False, allow_null=True)

    country = CountryField(name_only=True)

    class Meta:
        model = Profile
        fields = [
            "profile_photo",
            "phone_number",
            "university",
            "country",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def update(self, instance, validated_data):
        # Update the User model fields
        user = instance.user
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)

        # If password is provided, update it
        password = validated_data.get('password', None)
        if password:
            user.set_password(password)

        user.save()

        # Update the Profile model fields
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.university = validated_data.get('university', instance.university)
        instance.country = validated_data.get('country', instance.country)
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)

        instance.save()

        return instance

class FollowingSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "profile_photo",
            "twitter_handle",
            "about_me",
        ]

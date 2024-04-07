import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from core_apps.users.serializers import UserSerializer

User = get_user_model()


@pytest.mark.django_db
def test_user_serializer(normal_user):
    serializer = UserSerializer(normal_user)
    assert "id" in serializer.data
    assert "email" in serializer.data
    assert "first_name" in serializer.data
    assert "last_name" in serializer.data



@pytest.mark.django_db
def test_to_representation_normal_user(normal_user):
    serializer = UserSerializer(normal_user)
    serialized_data = serializer.data
    assert "is_staff" in serialized_data
    assert serialized_data["is_staff"] is False

@pytest.mark.django_db
def test_to_representation_super_user(super_user):
    serializer = UserSerializer(super_user)
    serialized_data = serializer.data
    print(serialized_data)
    assert "is_staff" in serialized_data
    assert serialized_data["is_staff"] is True




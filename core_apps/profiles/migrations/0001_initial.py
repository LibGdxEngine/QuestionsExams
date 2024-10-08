# Generated by Django 5.0.1 on 2024-09-28 11:21

import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("questions", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteList",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "questions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="favorite_lists",
                        to="questions.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_lists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-updated_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        default="+250784123456",
                        max_length=30,
                        region=None,
                        verbose_name="phone number",
                    ),
                ),
                (
                    "university",
                    models.TextField(
                        blank=True,
                        default="Your University",
                        max_length=180,
                        null=True,
                        verbose_name="university",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("male", "male"),
                            ("female", "female"),
                            ("other", "other"),
                        ],
                        default="other",
                        max_length=20,
                        verbose_name="gender",
                    ),
                ),
                (
                    "country",
                    django_countries.fields.CountryField(
                        default="KE", max_length=2, verbose_name="country"
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        default="Nairobi", max_length=180, verbose_name="city"
                    ),
                ),
                ("profile_photo", models.TextField()),
                (
                    "twitter_handle",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="twitter_handle"
                    ),
                ),
                (
                    "follows",
                    models.ManyToManyField(
                        blank=True, related_name="followed_by", to="profiles.profile"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-updated_at"],
                "abstract": False,
            },
        ),
    ]

import uuid
from random import randint

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.forms import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(verbose_name=_("first name"), max_length=50)
    last_name = models.CharField(verbose_name=_("last name"), max_length=50)
    email = models.EmailField(
        verbose_name=_("email address"), db_index=True, unique=True
    )
    email_activation_code = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def get_short_name(self):
        return f"{self.first_name.title()}"


class HomePageConfiguration(models.Model):
    video_url = models.CharField(max_length=255, help_text="URL of the video")
    description = models.TextField(help_text="Description of the video")
    questions = JSONField(help_text="List of questions and answers (JSON format)")

    def __str__(self):
        return "Video Configuration"  # Or a more descriptive name

    class Meta:
        verbose_name = "Video Configuration"
        verbose_name_plural = "Video Configurations" # if you expect to have more than one.



class ActivationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.activation_code:
            self.activation_code = randint(100000, 999999)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}"

    def create_activation_code(self):
        self.activation_code = randint(100000, 999999)
        self.last_sent = timezone.now()
        self.save()
        return self.activation_code

    def user_already_confirmed(self):
        return self.user.email_confirmed

    def verify_activation_code(self, code):
        if code == self.activation_code:
            self.user.email_confirmed = True
            self.user.save()
            return True
        return False

    def is_activation_code_valid(self, in_hours=24):
        if self.created_at is None:
            return False  # Or handle this case as needed
        expiration_time = self.created_at + timedelta(hours=in_hours)  # Valid for 24 hours
        return timezone.now() <= expiration_time

    def can_resend_code(self, in_minutes=1):
        if self.created_at is None:
            return True, timedelta()  # Allow resend if created_at is not set
        resend_wait_time = self.created_at + timedelta(minutes=in_minutes)  # Can resend every ? minutes
        current_time = timezone.now()
        can_resend = current_time >= resend_wait_time
        remaining_time = (resend_wait_time - current_time) if not can_resend else timedelta()
        return can_resend, remaining_time
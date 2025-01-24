from urllib.parse import urlsplit
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from allauth.account import app_settings as account_settings


def build_absolute_uri(request, location, protocol=None):
    """
    Helper to construct absolute URIs for links.
    Ensures the correct domain and removes any localhost/port issues.
    """
    if request is None:
        # Handle request=None by falling back to the Site framework
        if not app_settings.SITES_ENABLED:
            raise ImproperlyConfigured(
                "Passing `request=None` requires `django.contrib.sites` to be enabled."
            )
        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = f"{account_settings.DEFAULT_HTTP_PROTOCOL}://{site.domain}{location}"
        else:
            uri = location
    else:
        # Use the request to build the absolute URI
        uri = request.build_absolute_uri(location)

    # Force HTTPS protocol if not explicitly specified
    if protocol or account_settings.DEFAULT_HTTP_PROTOCOL == "https":
        protocol = protocol or account_settings.DEFAULT_HTTP_PROTOCOL
        uri = f"{protocol}:{uri.partition(':')[2]}"

    # Replace any localhost or 127.0.0.1 with the real domain
    uri = uri.replace("localhost", "krokplus.com").replace("127.0.0.1", "krokplus.com")

    # Remove any port in the URL
    uri = uri.split(":")[0] + uri.split(":")[2] if "://" in uri and ":" in uri else uri

    return uri


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation URL using the correct domain.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        return build_absolute_uri(request, url)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Sends the email confirmation, directly embedding the URL without templates.
        """
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        email_address = emailconfirmation.email_address.email

        # Direct email content
        subject = "KrokPlus: Confirm Your Email Address"
        body = (
            f"Hello,\n\n"
            f"Thank you for signing up on KrokPlus! Please confirm your email address "
            f"by clicking the link below:\n\n"
            f"{activate_url}\n\n"
            f"If you did not create this account, you can safely ignore this email.\n\n"
            f"Thank you,\nThe KrokPlus Team"
        )

        # Send the email
        self.send_mail(subject, email_address, {"message": body})

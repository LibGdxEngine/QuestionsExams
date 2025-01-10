import environ
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.static import static

from core_apps.users.views import health_check

env = environ.Env()

app_name = env("APP_NAME", default="Kroks")

schema_view = get_schema_view(
    openapi.Info(
        title="App API",
        default_version="v1",
        description="API endpoints for {} application".format(app_name),
        contact=openapi.Contact(email="ahmed.fathy1445@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
    path("admin/", admin.site.urls),
    # path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/health-check", health_check, name="health-check"),
    path("api/v1/user/", include("core_apps.users.urls", namespace="users")),
    path("social-auth/", include("social_django.urls", namespace="social")),
    # Articles
    path("api/v1/profiles/", include("core_apps.profiles.urls")),
    path("api/v1/articles/", include("core_apps.articles.urls")),
    path("api/v1/ratings/", include("core_apps.ratings.urls")),
    path("api/v1/bookmarks/", include("core_apps.bookmarks.urls")),
    path("api/v1/responses/", include("core_apps.responses.urls")),
    path("api/v1/elastic/", include("core_apps.search.urls")),
    path("api/v1/questions/", include("core_apps.questions.urls")),
    path("api/v2/questions/", include("core_apps.questions.urls_v2")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "{} Admin Panel".format(app_name)

admin.site.site_title = "{} ".format(app_name)

admin.site.index_title = "Welcome to {} admin portal".format(app_name)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .forms import UserChangeForm, UserCreationForm
from .models import User
from admincharts.admin import AdminChartMixin
from admincharts.utils import months_between_dates

from .resources import UserResource


class UserAdmin(AdminChartMixin, ImportExportModelAdmin, BaseUserAdmin):
    ordering = ["email"]
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    resource_class = UserResource

    list_display = [
        "pkid",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    ]

    list_display_links = ["pkid", "id", "email"]

    list_filter = ["is_staff", "is_active"]

    fieldsets = (
        (_("Login credentials"), {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions & Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important Date"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    search_fields = ["email", "first_name", "last_name"]

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}
        # Cannot reorder the queryset at this point
        earliest = min([x.date_joined for x in queryset])

        labels = []
        totals = []
        for b in months_between_dates(earliest, timezone.now()):
            labels.append(b.strftime("%b %Y"))
            totals.append(
                len(
                    [
                        x
                        for x in queryset
                        if x.date_joined.year == b.year and x.date_joined.month == b.month
                    ]
                )
            )

        return {
            "labels": labels,
            "datasets": [
                {"label": "New accounts per month", "data": totals, "backgroundColor": "#79aec8"},
            ],
        }


admin.site.register(User, UserAdmin)

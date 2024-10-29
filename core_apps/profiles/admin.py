from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "user", "phone_number", "country", "city"]
    list_display_links = ["pkid", "id", "user"]
    list_filter = ["country", "city"]


admin.site.register(Profile, ProfileAdmin)

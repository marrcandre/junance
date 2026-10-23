from django.contrib import admin

from identity.models import Family, FamilyMember


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ["family", "user", "role", "joined_at"]
    list_filter = ["role"]
    search_fields = ["family__name", "user__username"]

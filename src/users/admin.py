from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("username",)}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("주요 정보", {"fields": ("last_login", "created_at")}),
    )

    list_display = ("email", "username", "is_staff", "is_active", "created_at")
    search_fields = ("email", "username",)
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)

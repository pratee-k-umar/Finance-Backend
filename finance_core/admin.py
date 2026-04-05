from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from finance_core.models import FinancialRecord, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    search_fields = ["name"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "status", "date_joined"]
    list_filter = ["role", "status", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Role and Status"), {"fields": ("role", "status")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "amount",
        "record_type",
        "category",
        "date",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["record_type", "category", "date", "is_deleted", "created_at"]
    search_fields = ["user__username", "category", "notes"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        (
            "Transaction Details",
            {"fields": ("amount", "record_type", "category", "date")},
        ),
        ("Additional Info", {"fields": ("notes", "is_deleted")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user, is_deleted=False)
        return queryset

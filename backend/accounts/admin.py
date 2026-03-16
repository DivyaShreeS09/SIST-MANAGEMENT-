from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ApproverAssignment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "full_name",
        "role",
        "program",
        "section",
        "year",
        "department",
        "hosteller",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": (
                "full_name",
                "role",
                "register_no",
                "program",
                "section",
                "year",
                "department",
                "hosteller",
                "student_photo",
            )
        }),
    )


@admin.register(ApproverAssignment)
class ApproverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("approver", "role", "program", "year", "section")
    list_filter = ("role", "program", "year", "section")
    search_fields = ("approver__username", "approver__full_name", "program", "section")
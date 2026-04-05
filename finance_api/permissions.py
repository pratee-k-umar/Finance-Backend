from finance_core.models import Role
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsActive(BasePermission):
    """Check if user is active"""

    message = "Your account is inactive. Please contact an administrator."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.status == "active"
        )


class IsViewer(BasePermission):
    """Check if user is a Viewer"""

    def has_permission(self, request, view):
        return request.user.role.name == Role.VIEWER


class IsAnalyst(BasePermission):
    """Check if user is an Analyst"""

    def has_permission(self, request, view):
        return request.user.role.name == Role.ANALYST


class IsAdmin(BasePermission):
    """Check if user is an Admin"""

    def has_permission(self, request, view):
        return request.user.role.name == Role.ADMIN


class IsAdminOrAnalyst(BasePermission):
    """Check if user is Admin or Analyst"""

    def has_permission(self, request, view):
        return request.user.role.name in [Role.ADMIN, Role.ANALYST]


class CanViewFinancialRecords(BasePermission):
    """
    Viewer, Analyst, and Admin can view records.
    - Viewers see only their own records
    - Analysts see only their own records
    - Admins see all records
    """

    def has_permission(self, request, view):
        return request.user.role.name in [Role.VIEWER, Role.ANALYST, Role.ADMIN]

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == Role.ADMIN:
            return True
        return obj.user == request.user


class CanCreateFinancialRecords(BasePermission):
    """
    Only Analyst and Admin can create records
    """

    message = "You don't have permission to create financial records."

    def has_permission(self, request, view):
        return request.user.role.name in [Role.ANALYST, Role.ADMIN]


class CanModifyFinancialRecords(BasePermission):
    """
    Analyst can modify only their own records.
    Admin can modify all records.
    """

    message = "You don't have permission to modify this record."

    def has_permission(self, request, view):
        return request.user.role.name in [Role.ANALYST, Role.ADMIN]

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == Role.ADMIN:
            return True
        if request.user.role.name == Role.ANALYST:
            return obj.user == request.user
        return False


class CanManageUsers(BasePermission):
    """
    Only Admin can manage users
    """

    message = "You don't have permission to manage users."

    def has_permission(self, request, view):
        return request.user.role.name == Role.ADMIN


class CanViewDashboard(BasePermission):
    """
    Viewer, Analyst, and Admin can view dashboard data.
    - Viewers see only their own summary
    - Analysts see only their own summary
    - Admins can view summaries for all users or specific users
    """

    def has_permission(self, request, view):
        return request.user.role.name in [Role.VIEWER, Role.ANALYST, Role.ADMIN]

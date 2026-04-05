import calendar
from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from finance_core.models import (
    Budget,
    BudgetAlert,
    EmailNotification,
    FinancialRecord,
    RecurringTransaction,
    Role,
    User,
    Webhook,
    WebhookEvent,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .csv_export import (
    export_budget_summary_to_csv,
    export_financial_records_to_csv,
    export_recurring_transactions_to_csv,
)
from .permissions import (
    CanCreateFinancialRecords,
    CanManageUsers,
    CanModifyFinancialRecords,
    CanViewDashboard,
    CanViewFinancialRecords,
    IsActive,
    IsAdmin,
    IsAnalyst,
)
from .serializers import (
    BudgetAlertSerializer,
    BudgetSerializer,
    CategorySummarySerializer,
    DashboardSummarySerializer,
    EmailNotificationSerializer,
    FinancialRecordCreateSerializer,
    FinancialRecordSerializer,
    MonthlySummarySerializer,
    RecurringTransactionSerializer,
    RoleSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    WebhookEventSerializer,
    WebhookSerializer,
)
from .utils import (
    send_budget_alert_email,
    trigger_budget_alert_webhook,
    trigger_webhook,
)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for roles (read-only)"""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsActive]

    @action(detail=False, methods=["get"])
    def choices(self, request):
        """Get available role choices"""
        choices = Role.ROLE_CHOICES
        return Response(
            {
                "choices": [
                    {"value": choice[0], "label": choice[1]} for choice in choices
                ]
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for user management"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        """
        Viewers and Analysts can only see themselves.
        Admins can see all users.
        """
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """Set permissions per action"""
        if self.action == "create":
            return [IsAuthenticated(), IsActive(), IsAdmin()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsActive(), IsAdmin()]
        elif self.action == "list":
            return [IsAuthenticated(), IsActive(), IsAdmin()]
        elif self.action == "retrieve":
            return [IsAuthenticated(), IsActive(), IsAdmin()]
        return [IsAuthenticated(), IsActive()]

    def create(self, request, *args, **kwargs):
        """Create a new user (Admin only)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a user (Admin only)"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        """Change user status (Admin only)"""
        if request.user.role.name != Role.ADMIN:
            return Response(
                {"error": "Only admins can change user status"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = self.get_object()
        new_status = request.data.get("status")
        if new_status not in ["active", "inactive"]:
            return Response(
                {"error": "Invalid status. Must be active or inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.status = new_status
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def change_role(self, request, pk=None):
        """Change user role (Admin only)"""
        if request.user.role.name != Role.ADMIN:
            return Response(
                {"error": "Only admins can change user roles"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = self.get_object()
        role_id = request.data.get("role_id")
        try:
            role = Role.objects.get(id=role_id)
            user.role = role
            user.save()
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND
            )


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """API endpoint for financial records CRUD operations"""

    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        """
        Filter records based on user role:
        - Viewer/Analyst: See only their own records
        - Admin: See all records (unless filtered)
        """
        user = self.request.user
        queryset = FinancialRecord.objects.filter(is_deleted=False)

        if user.role.name == Role.ADMIN:
            # Admin can see all records and can filter by user_id
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            # Viewer and Analyst see only their own records
            queryset = queryset.filter(user=user)

        # Additional filters
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        record_type = self.request.query_params.get("type")
        if record_type:
            queryset = queryset.filter(record_type=record_type)

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return FinancialRecordCreateSerializer
        return FinancialRecordSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsActive(), CanCreateFinancialRecords()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsActive(), CanModifyFinancialRecords()]
        return [IsAuthenticated(), IsActive(), CanViewFinancialRecords()]

    def create(self, request, *args, **kwargs):
        """Create a financial record (Analyst and Admin only)"""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """Update a financial record"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Check permissions
        if request.user.role.name == Role.ANALYST and instance.user != request.user:
            return Response(
                {"error": "You can only update your own records"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a financial record (soft delete)"""
        instance = self.get_object()

        if request.user.role.name == Role.ANALYST and instance.user != request.user:
            return Response(
                {"error": "You can only delete your own records"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsActive, CanViewDashboard],
    )
    def summary(self, request):
        """Get dashboard summary for current user or specified user (Admin only)"""
        # Determine which user's records to summarize
        user = request.user
        summary_user_id = request.query_params.get("user_id")
        if summary_user_id and user.role.name == Role.ADMIN:
            try:
                user = User.objects.get(id=summary_user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        elif summary_user_id and user.role.name != Role.ADMIN:
            return Response(
                {"error": "Only admins can view other users summaries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = FinancialRecord.objects.filter(user=user, is_deleted=False)

        # Get filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Calculate totals
        income_agg = queryset.filter(record_type="income").aggregate(
            total=Sum("amount")
        )
        expense_agg = queryset.filter(record_type="expense").aggregate(
            total=Sum("amount")
        )

        total_income = income_agg["total"] or Decimal("0.00")
        total_expenses = expense_agg["total"] or Decimal("0.00")
        net_balance = total_income - total_expenses

        # Category breakdown
        category_breakdown = {}
        categories = queryset.values("category").distinct()
        for cat in categories:
            category = cat["category"]
            income = queryset.filter(category=category, record_type="income").aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0.00")
            expense = queryset.filter(
                category=category, record_type="expense"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            category_breakdown[category] = {
                "income": float(income),
                "expense": float(expense),
                "net": float(income - expense),
            }

        # Recent records
        recent_records = queryset[:10]
        recent_serializer = FinancialRecordSerializer(recent_records, many=True)

        summary_data = {
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_balance": float(net_balance),
            "category_breakdown": category_breakdown,
            "recent_records": recent_serializer.data,
            "record_count": queryset.count(),
            "date_range": {
                "start_date": start_date or "All time",
                "end_date": end_date or "Today",
            },
        }

        return Response(summary_data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsActive, CanViewDashboard],
    )
    def category_summary(self, request):
        """Get category-wise summary"""
        user = request.user
        summary_user_id = request.query_params.get("user_id")
        if summary_user_id and user.role.name == Role.ADMIN:
            try:
                user = User.objects.get(id=summary_user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        elif summary_user_id and user.role.name != Role.ADMIN:
            return Response(
                {"error": "Only admins can view other users summaries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = FinancialRecord.objects.filter(user=user, is_deleted=False)

        # Get filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Category-wise breakdown
        categories = queryset.values("category").distinct()
        category_summaries = []

        for cat in categories:
            category = cat["category"]
            income = queryset.filter(category=category, record_type="income").aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0.00")
            expense = queryset.filter(
                category=category, record_type="expense"
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            net = income - expense

            category_summaries.append(
                {
                    "category": category,
                    "total_income": float(income),
                    "total_expenses": float(expense),
                    "net": float(net),
                    "record_count": queryset.filter(category=category).count(),
                }
            )

        return Response(category_summaries)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsActive, CanViewDashboard],
    )
    def monthly_trends(self, request):
        """Get monthly income/expense trends"""
        user = request.user
        summary_user_id = request.query_params.get("user_id")
        if summary_user_id and user.role.name == Role.ADMIN:
            try:
                user = User.objects.get(id=summary_user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        elif summary_user_id and user.role.name != Role.ADMIN:
            return Response(
                {"error": "Only admins can view other users summaries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = FinancialRecord.objects.filter(user=user, is_deleted=False)

        # Get months parameter (default: last 12 months)
        months_param = request.query_params.get("months", 12)
        try:
            months_param = int(months_param)
        except (ValueError, TypeError):
            months_param = 12

        # Calculate date range
        today = timezone.now().date()
        start_date = today - timedelta(days=30 * months_param)
        queryset = queryset.filter(date__gte=start_date)

        # Group by month
        monthly_data = {}
        for i in range(months_param, 0, -1):
            month_date = today - timedelta(days=30 * (i - 1))
            month_key = month_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "total_income": Decimal("0.00"),
                    "total_expenses": Decimal("0.00"),
                    "net": Decimal("0.00"),
                }

        # Populate data
        for record in queryset:
            month_key = record.date.strftime("%Y-%m")
            if month_key in monthly_data:
                if record.record_type == "income":
                    monthly_data[month_key]["total_income"] += record.amount
                else:
                    monthly_data[month_key]["total_expenses"] += record.amount

        # Calculate net and convert to float
        for month_key in monthly_data:
            monthly_data[month_key]["net"] = (
                monthly_data[month_key]["total_income"]
                - monthly_data[month_key]["total_expenses"]
            )
            monthly_data[month_key]["total_income"] = float(
                monthly_data[month_key]["total_income"]
            )
            monthly_data[month_key]["total_expenses"] = float(
                monthly_data[month_key]["total_expenses"]
            )
            monthly_data[month_key]["net"] = float(monthly_data[month_key]["net"])

        return Response(list(monthly_data.values()))

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """Export financial records as CSV"""
        user = request.user

        # Build filters from query params
        filters = {}
        if request.query_params.get("date_from"):
            filters["date_from"] = request.query_params.get("date_from")
        if request.query_params.get("date_to"):
            filters["date_to"] = request.query_params.get("date_to")
        if request.query_params.get("category"):
            filters["category"] = request.query_params.get("category")
        if request.query_params.get("type"):
            filters["record_type"] = request.query_params.get("type")

        csv_content = export_financial_records_to_csv(user, filters)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="financial_records.csv"'
        response.write(csv_content)
        return response


class BudgetViewSet(viewsets.ModelViewSet):
    """API endpoint for budget management"""

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return Budget.objects.all()
        return Budget.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """Export budgets as CSV"""
        csv_content = export_budget_summary_to_csv(request.user)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="budgets.csv"'
        response.write(csv_content)
        return response


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    """API endpoint for recurring transactions"""

    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return RecurringTransaction.objects.all()
        return RecurringTransaction.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """Export recurring transactions as CSV"""
        csv_content = export_recurring_transactions_to_csv(request.user)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="recurring_transactions.csv"'
        )
        response.write(csv_content)
        return response


class WebhookViewSet(viewsets.ModelViewSet):
    """API endpoint for webhook management"""

    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return Webhook.objects.all()
        return Webhook.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Test webhook by sending a test payload"""
        webhook = self.get_object()

        test_data = {
            "event_type": webhook.event_type,
            "timestamp": timezone.now().isoformat(),
            "data": {"test": True, "message": "This is a test webhook event"},
        }

        trigger_webhook(webhook, test_data["data"])
        return Response({"status": "Test webhook sent"})

    @action(detail=False, methods=["get"])
    def events(self, request):
        """Get webhook events for all user webhooks"""
        user = request.user
        webhooks = Webhook.objects.filter(user=user)
        events = WebhookEvent.objects.filter(webhook__in=webhooks).order_by(
            "-created_at"
        )[:100]
        serializer = WebhookEventSerializer(events, many=True)
        return Response(serializer.data)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing webhook events"""

    serializer_class = WebhookEventSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return WebhookEvent.objects.all()
        webhooks = Webhook.objects.filter(user=user)
        return WebhookEvent.objects.filter(webhook__in=webhooks)


class EmailNotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for email notification preferences"""

    serializer_class = EmailNotificationSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return EmailNotification.objects.all()
        return EmailNotification.objects.filter(user=user)

    @action(detail=False, methods=["get"])
    def my_preferences(self, request):
        """Get current user's email notification preferences"""
        try:
            email_notification = request.user.email_notifications
        except EmailNotification.DoesNotExist:
            email_notification = EmailNotification.objects.create(user=request.user)

        serializer = self.get_serializer(email_notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def update_preferences(self, request):
        """Update current user's email notification preferences"""
        try:
            email_notification = request.user.email_notifications
        except EmailNotification.DoesNotExist:
            email_notification = EmailNotification.objects.create(user=request.user)

        serializer = self.get_serializer(
            email_notification, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BudgetAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing budget alerts"""

    serializer_class = BudgetAlertSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == Role.ADMIN:
            return BudgetAlert.objects.all()
        budgets = Budget.objects.filter(user=user)
        return BudgetAlert.objects.filter(budget__in=budgets)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        """Dismiss a budget alert"""
        alert = self.get_object()
        if alert.budget.user != request.user and request.user.role.name != Role.ADMIN:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        alert.status = "dismissed"
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

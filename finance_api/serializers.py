from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
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
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.get_name_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_name",
            "status",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "role",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.get_name_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_name",
            "status",
        ]
        read_only_fields = ["id", "username"]


class FinancialRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    record_type_display = serializers.CharField(
        source="get_record_type_display", read_only=True
    )

    class Meta:
        model = FinancialRecord
        fields = [
            "id",
            "user",
            "username",
            "amount",
            "record_type",
            "record_type_display",
            "category",
            "date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "username", "created_at", "updated_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_date(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

    def validate_category(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category cannot be empty.")
        return value


class FinancialRecordCreateSerializer(FinancialRecordSerializer):
    """Serializer for creating financial records"""

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""

    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    category_breakdown = serializers.DictField()
    recent_records = FinancialRecordSerializer(many=True)
    record_count = serializers.IntegerField()
    date_range = serializers.DictField()


class CategorySummarySerializer(serializers.Serializer):
    """Serializer for category-wise summary"""

    category = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)
    record_count = serializers.IntegerField()


class MonthlySummarySerializer(serializers.Serializer):
    """Serializer for monthly trends"""

    month = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)


# Advanced Features Serializers


class BudgetSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    spent_amount = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "user",
            "category",
            "limit_amount",
            "frequency",
            "frequency_display",
            "alert_at_percentage",
            "spent_amount",
            "remaining",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "user", "spent_amount", "remaining", "created_at"]

    def get_spent_amount(self, obj):
        from datetime import date, timedelta

        from django.db.models import Sum
        from django.utils import timezone

        today = timezone.now().date()
        if obj.frequency == "monthly":
            start_date = date(today.year, today.month, 1)
        elif obj.frequency == "yearly":
            start_date = date(today.year, 1, 1)
        else:  # quarterly
            quarter = (today.month - 1) // 3
            start_date = date(today.year, quarter * 3 + 1, 1)

        spent = (
            FinancialRecord.objects.filter(
                user=obj.user,
                category=obj.category,
                record_type="expense",
                date__gte=start_date,
                is_deleted=False,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return spent

    def get_remaining(self, obj):
        spent = self.get_spent_amount(obj)
        return obj.limit_amount - spent


class RecurringTransactionSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    record_type_display = serializers.CharField(
        source="get_record_type_display", read_only=True
    )

    class Meta:
        model = RecurringTransaction
        fields = [
            "id",
            "user",
            "amount",
            "record_type",
            "record_type_display",
            "category",
            "frequency",
            "frequency_display",
            "next_date",
            "end_date",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class WebhookSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(
        source="get_event_type_display", read_only=True
    )

    class Meta:
        model = Webhook
        fields = [
            "id",
            "user",
            "url",
            "event_type",
            "event_type_display",
            "is_active",
            "secret",
            "created_at",
        ]
        read_only_fields = ["id", "user", "secret", "created_at"]


class WebhookEventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = WebhookEvent
        fields = [
            "id",
            "webhook",
            "payload",
            "status",
            "status_display",
            "response_status",
            "response_body",
            "error_message",
            "attempts",
            "last_attempt_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "webhook",
            "status",
            "response_status",
            "response_body",
            "error_message",
            "last_attempt_at",
            "created_at",
        ]


class EmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotification
        fields = [
            "id",
            "user",
            "budget_alerts",
            "record_notifications",
            "monthly_summary",
            "recurring_alerts",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class BudgetAlertSerializer(serializers.ModelSerializer):
    budget_category = serializers.CharField(source="budget.category", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = BudgetAlert
        fields = [
            "id",
            "budget",
            "budget_category",
            "spent_amount",
            "percentage_used",
            "status",
            "status_display",
            "created_at",
            "sent_at",
        ]
        read_only_fields = ["id", "status", "sent_at", "created_at"]

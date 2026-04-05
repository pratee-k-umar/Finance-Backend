import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.core.validators import (MinValueValidator, URLValidator,
                                    ValidationError)
from django.db import models
from django.utils import timezone


def validate_percentage(value):
    """Validate that value is between 0 and 100"""
    if not (0 <= value <= 100):
        raise ValidationError("Percentage must be between 0 and 100")


class Role(models.Model):
    """User role definitions"""

    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (VIEWER, "Viewer"),
        (ANALYST, "Analyst"),
        (ADMIN, "Admin"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class UserManager(DefaultUserManager):
    """Custom manager for User model"""

    def create_superuser(self, username, email, password, **extra_fields):
        """Create superuser with default admin role"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Get or create the admin role
        admin_role, _ = Role.objects.get_or_create(
            name=Role.ADMIN, defaults={"description": "Admin role"}
        )
        extra_fields["role"] = admin_role

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Extended user model with role and status"""

    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users", null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )

    objects = UserManager()

    class Meta:
        ordering = ["date_joined"]

    def __str__(self):
        return f"{self.username} ({self.role.get_name_display() if self.role else 'No Role'})"


class FinancialRecord(models.Model):
    """Financial transaction/entry records"""

    TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="financial_records"
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    record_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-date"]),
            models.Index(fields=["user", "record_type"]),
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_record_type_display()} ${self.amount} ({self.date})"

    def delete(self, *args, **kwargs):
        """Soft delete"""
        self.is_deleted = True
        self.save()

    def hard_delete(self, *args, **kwargs):
        """Permanent delete"""
        super().delete(*args, **kwargs)
        super().delete(*args, **kwargs)


class Budget(models.Model):
    """Budget tracking for users"""

    FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("quarterly", "Quarterly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.CharField(max_length=100)
    limit_amount = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="monthly")
    alert_at_percentage = models.IntegerField(
        default=80, validators=[MinValueValidator(0), validate_percentage]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category"]
        unique_together = ["user", "category", "frequency"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.category} Budget (${self.limit_amount})"


class RecurringTransaction(models.Model):
    """Recurring/recurring transactions"""

    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("biweekly", "Biweekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recurring_transactions"
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    record_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    next_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_date"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["next_date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - Recurring {self.get_record_type_display()} ${self.amount} ({self.frequency})"


class Webhook(models.Model):
    """Webhook configurations for users"""

    EVENT_CHOICES = [
        ("record_created", "Record Created"),
        ("record_updated", "Record Updated"),
        ("record_deleted", "Record Deleted"),
        ("budget_exceeded", "Budget Exceeded"),
        ("alert_triggered", "Alert Triggered"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="webhooks"
    )
    url = models.URLField()
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=255, unique=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "url", "event_type"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_event_type_display()} Webhook"


class WebhookEvent(models.Model):
    """Log of webhook events sent"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(
        Webhook, on_delete=models.CASCADE, related_name="events"
    )
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["webhook", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"WebhookEvent {self.id} - {self.status}"


class EmailNotification(models.Model):
    """Email notification settings"""

    NOTIFICATION_TYPE_CHOICES = [
        ("budget_alert", "Budget Alert"),
        ("record_created", "Record Created"),
        ("monthly_summary", "Monthly Summary"),
        ("recurring_transaction", "Recurring Transaction"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_notifications"
    )
    budget_alerts = models.BooleanField(default=True)
    record_notifications = models.BooleanField(default=True)
    monthly_summary = models.BooleanField(default=True)
    recurring_alerts = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Email Notifications"

    def __str__(self):
        return f"Email Notifications for {self.user.username}"


class BudgetAlert(models.Model):
    """Track budget alert history"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("dismissed", "Dismissed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="alerts"
    )
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2)
    percentage_used = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["budget", "status"]),
        ]

    def __str__(self):
        return f"Alert for {self.budget.category} - {self.percentage_used}% used"
        return f"Alert for {self.budget.category} - {self.percentage_used}% used"
        return f"Alert for {self.budget.category} - {self.percentage_used}% used"

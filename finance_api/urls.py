from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BudgetAlertViewSet,
    BudgetViewSet,
    EmailNotificationViewSet,
    FinancialRecordViewSet,
    RecurringTransactionViewSet,
    RoleViewSet,
    UserViewSet,
    WebhookEventViewSet,
    WebhookViewSet,
)

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")
router.register(
    r"financial-records", FinancialRecordViewSet, basename="financial-record"
)
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(
    r"recurring-transactions",
    RecurringTransactionViewSet,
    basename="recurring-transaction",
)
router.register(r"webhooks", WebhookViewSet, basename="webhook")
router.register(r"webhook-events", WebhookEventViewSet, basename="webhook-event")
router.register(
    r"email-notifications", EmailNotificationViewSet, basename="email-notification"
)
router.register(r"budget-alerts", BudgetAlertViewSet, basename="budget-alert")

urlpatterns = [
    path("", include(router.urls)),
]

from datetime import date

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from finance_api.utils import (send_budget_alert_email,
                               trigger_budget_alert_webhook)
from finance_core.models import (Budget, BudgetAlert, EmailNotification,
                                 FinancialRecord)


class Command(BaseCommand):
    help = "Check budgets and send alerts if spending exceeds thresholds"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Checking budgets and processing alerts..."))
        
        active_budgets = Budget.objects.filter(is_active=True)
        alerts_sent = 0
        budgets_checked = 0
        
        for budget in active_budgets:
            budgets_checked += 1
            today = timezone.now().date()
            
            # Calculate period start date based on frequency
            if budget.frequency == "monthly":
                start_date = date(today.year, today.month, 1)
            elif budget.frequency == "yearly":
                start_date = date(today.year, 1, 1)
            else:  # quarterly
                quarter = (today.month - 1) // 3
                start_date = date(today.year, quarter * 3 + 1, 1)
            
            # Calculate spent amount
            spent = FinancialRecord.objects.filter(
                user=budget.user,
                category=budget.category,
                record_type="expense",
                date__gte=start_date,
                date__lte=today,
                is_deleted=False,
            ).aggregate(total=Sum("amount"))["total"] or 0
            
            # Calculate percentage used
            if budget.limit_amount > 0:
                percentage_used = int((float(spent) / float(budget.limit_amount)) * 100)
            else:
                percentage_used = 0
            
            # Check if alert should be sent
            if percentage_used >= budget.alert_at_percentage:
                # Check if we already have an unsent alert for this period
                existing_alert = BudgetAlert.objects.filter(
                    budget=budget,
                    status__in=["pending", "sent"],
                    created_at__date=today,
                ).exists()
                
                if not existing_alert:
                    # Create alert record
                    alert = BudgetAlert.objects.create(
                        budget=budget,
                        spent_amount=spent,
                        percentage_used=percentage_used,
                        status="pending",
                    )
                    
                    # Send email notification if enabled
                    try:
                        email_settings = budget.user.email_notifications
                        should_send_email = email_settings.budget_alerts
                    except:
                        should_send_email = True  # Default to sending if no settings
                    
                    if should_send_email:
                        if send_budget_alert_email(budget.user, budget, spent, percentage_used):
                            alert.status = "sent"
                            alert.sent_at = timezone.now()
                    
                    alert.save()
                    
                    # Trigger webhook
                    trigger_budget_alert_webhook(
                        budget.user,
                        budget,
                        spent,
                        percentage_used
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Budget alert sent: {budget.user.username} - {budget.category} "
                            f"({percentage_used}% of ${budget.limit_amount})"
                        )
                    )
                    alerts_sent += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Budget check completed! Checked: {budgets_checked}, Alerts sent: {alerts_sent}"
            )
        )
                f"\n✓ Budget check completed! Checked: {budgets_checked}, Alerts sent: {alerts_sent}"
            )
        )

"""
Celery tasks for finance_api
"""

from celery import shared_task
from django.core.management import call_command


@shared_task
def process_recurring_transactions_task():
    """
    Task to process recurring transactions and create new financial records.
    Scheduled to run daily at midnight.
    """
    try:
        call_command("process_recurring_transactions")
        return "Recurring transactions processed successfully"
    except Exception as e:
        return f"Error processing recurring transactions: {str(e)}"


@shared_task
def check_budgets_task():
    """
    Task to check budgets and send alerts if thresholds are exceeded.
    Scheduled to run daily at 9 AM.
    """
    try:
        call_command("check_budgets")
        return "Budget checks completed successfully"
    except Exception as e:
        return f"Error checking budgets: {str(e)}"

"""
CSV export functionality for financial records
"""

import csv
from io import StringIO

from django.utils import timezone
from finance_core.models import FinancialRecord


def export_financial_records_to_csv(user, filters=None):
    """
    Export user's financial records to CSV

    Args:
        user: User object
        filters: Dictionary of filters (date_from, date_to, category, record_type)

    Returns:
        CSV string
    """
    records = FinancialRecord.objects.filter(user=user, is_deleted=False)

    if filters:
        if filters.get("date_from"):
            records = records.filter(date__gte=filters["date_from"])
        if filters.get("date_to"):
            records = records.filter(date__lte=filters["date_to"])
        if filters.get("category"):
            records = records.filter(category=filters["category"])
        if filters.get("record_type"):
            records = records.filter(record_type=filters["record_type"])

    records = records.order_by("-date", "-created_at")

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(
        [
            "Date",
            "Type",
            "Category",
            "Amount",
            "Notes",
            "Created At",
        ]
    )

    # Data rows
    for record in records:
        writer.writerow(
            [
                record.date.isoformat(),
                record.get_record_type_display(),
                record.category,
                str(record.amount),
                record.notes or "",
                record.created_at.isoformat(),
            ]
        )

    # Summary rows
    writer.writerow([])  # Blank row
    writer.writerow(["Summary", "", "", "", "", ""])

    total_income = (
        records.filter(record_type="income")
        .values_list("amount", flat=True)
        .aggregate(
            total=__import__("django.db.models", fromlist=["Sum"]).Sum("amount")
        )["total"]
        or 0
    )

    total_expenses = (
        records.filter(record_type="expense")
        .values_list("amount", flat=True)
        .aggregate(
            total=__import__("django.db.models", fromlist=["Sum"]).Sum("amount")
        )["total"]
        or 0
    )

    net = total_income - total_expenses

    writer.writerow(["Total Income", "", "", str(total_income), "", ""])
    writer.writerow(["Total Expenses", "", "", str(total_expenses), "", ""])
    writer.writerow(["Net Balance", "", "", str(net), "", ""])
    writer.writerow(["Record Count", "", "", str(records.count()), "", ""])
    writer.writerow(["Export Date", "", "", timezone.now().isoformat(), "", ""])

    return output.getvalue()


def export_budget_summary_to_csv(user):
    """
    Export user's budget summary to CSV

    Args:
        user: User object

    Returns:
        CSV string
    """
    from datetime import date

    from django.db.models import Sum
    from finance_core.models import Budget

    budgets = Budget.objects.filter(user=user, is_active=True)

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(
        [
            "Category",
            "Limit Amount",
            "Frequency",
            "Spent Amount",
            "Percentage Used",
            "Remaining",
            "Alert Threshold %",
            "Status",
        ]
    )

    # Data rows
    for budget in budgets:
        # Calculate spent amount
        today = timezone.now().date()
        if budget.frequency == "monthly":
            start_date = date(today.year, today.month, 1)
        elif budget.frequency == "yearly":
            start_date = date(today.year, 1, 1)
        else:  # quarterly
            quarter = (today.month - 1) // 3
            start_date = date(today.year, quarter * 3 + 1, 1)

        spent = (
            FinancialRecord.objects.filter(
                user=user,
                category=budget.category,
                record_type="expense",
                date__gte=start_date,
                is_deleted=False,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        percentage = (
            int((float(spent) / float(budget.limit_amount) * 100))
            if budget.limit_amount > 0
            else 0
        )
        remaining = budget.limit_amount - spent
        status = "Alert" if percentage >= budget.alert_at_percentage else "OK"

        writer.writerow(
            [
                budget.category,
                str(budget.limit_amount),
                budget.get_frequency_display(),
                str(spent),
                f"{percentage}%",
                str(remaining),
                f"{budget.alert_at_percentage}%",
                status,
            ]
        )

    writer.writerow([])
    writer.writerow(["Export Date", "", "", timezone.now().isoformat(), "", "", "", ""])

    return output.getvalue()


def export_recurring_transactions_to_csv(user):
    """
    Export user's recurring transactions to CSV

    Args:
        user: User object

    Returns:
        CSV string
    """
    from finance_core.models import RecurringTransaction

    transactions = RecurringTransaction.objects.filter(user=user, is_active=True)

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(
        [
            "Type",
            "Category",
            "Amount",
            "Frequency",
            "Next Date",
            "End Date",
            "Description",
            "Created At",
        ]
    )

    # Data rows
    for transaction in transactions:
        writer.writerow(
            [
                transaction.get_record_type_display(),
                transaction.category,
                str(transaction.amount),
                transaction.get_frequency_display(),
                transaction.next_date.isoformat(),
                transaction.end_date.isoformat() if transaction.end_date else "",
                transaction.description or "",
                transaction.created_at.isoformat(),
            ]
        )

    writer.writerow([])
    writer.writerow(["Export Date", "", "", timezone.now().isoformat(), "", "", "", ""])

    return output.getvalue()

    return output.getvalue()

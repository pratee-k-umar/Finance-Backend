from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from finance_core.models import FinancialRecord, RecurringTransaction


class Command(BaseCommand):
    help = "Process recurring transactions and create corresponding financial records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to look ahead for processing recurring transactions (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without actually creating records",
        )

    def handle(self, *args, **options):
        days_ahead = options["days"]
        dry_run = options["dry_run"]

        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)

        self.stdout.write(
            self.style.SUCCESS(
                f"Processing recurring transactions through {end_date}..."
            )
        )

        active_transactions = RecurringTransaction.objects.filter(
            is_active=True,
            next_date__lte=end_date,
        ).exclude(end_date__lt=today)

        total_created = 0

        for transaction in active_transactions:
            # Calculate how many times this should occur
            current_date = transaction.next_date

            while current_date <= end_date:
                if transaction.end_date and current_date > transaction.end_date:
                    break

                if not dry_run:
                    # Create the financial record
                    FinancialRecord.objects.create(
                        user=transaction.user,
                        amount=transaction.amount,
                        record_type=transaction.record_type,
                        category=transaction.category,
                        date=current_date,
                        notes=f"Auto-generated from recurring transaction: {transaction.description}",
                    )
                    total_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Created {transaction.record_type} record for {transaction.user.username} "
                            f"({transaction.category}, ${transaction.amount}) on {current_date}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"  [DRY RUN] Would create {transaction.record_type} record for {transaction.user.username} "
                        f"({transaction.category}, ${transaction.amount}) on {current_date}"
                    )

                # Calculate next occurrence
                current_date = self._get_next_date(current_date, transaction.frequency)
                total_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Recurring transaction processing completed! "
                f"Total{' [DRY RUN]' if dry_run else ''}: {total_created} records"
            )
        )

    def _get_next_date(self, current_date, frequency):
        """Calculate the next occurrence date based on frequency"""
        if frequency == "daily":
            return current_date + timedelta(days=1)
        elif frequency == "weekly":
            return current_date + timedelta(weeks=1)
        elif frequency == "biweekly":
            return current_date + timedelta(weeks=2)
        elif frequency == "monthly":
            # Simple month increment (doesn't handle month-end edge cases)
            if current_date.month == 12:
                return date(current_date.year + 1, 1, min(current_date.day, 1))
            else:
                try:
                    return current_date.replace(month=current_date.month + 1)
                except ValueError:
                    # Day doesn't exist in next month (e.g., Jan 31 -> Feb)
                    return date(
                        current_date.year, current_date.month + 1, 1
                    ) + timedelta(days=current_date.day - 1)
        elif frequency == "quarterly":
            month = current_date.month + 3
            year = current_date.year
            if month > 12:
                month -= 12
                year += 1
            try:
                return current_date.replace(year=year, month=month)
            except ValueError:
                return date(year, month if month <= 12 else month - 12, 1) + timedelta(
                    days=current_date.day - 1
                )
        elif frequency == "yearly":
            try:
                return current_date.replace(year=current_date.year + 1)
            except ValueError:
                # Feb 29 in leap year
                return date(current_date.year + 1, 3, 1)

        return current_date
        return current_date

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from finance_core.models import FinancialRecord, User


class Command(BaseCommand):
    help = "Seed sample financial records for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of records to create per user (default: 50)",
        )

    def handle(self, *args, **options):
        record_count = options["count"]

        # Income categories and amounts
        income_categories = [
            ("Salary", Decimal("3500.00")),
            ("Freelance Work", Decimal("500.00")),
            ("Investment Returns", Decimal("250.00")),
            ("Bonus", Decimal("1000.00")),
            ("Side Hustle", Decimal("300.00")),
        ]

        # Expense categories and typical amounts
        expense_categories = [
            ("Groceries", Decimal("120.00")),
            ("Rent", Decimal("1200.00")),
            ("Utilities", Decimal("150.00")),
            ("Transportation", Decimal("80.00")),
            ("Dining Out", Decimal("45.00")),
            ("Entertainment", Decimal("60.00")),
            ("Healthcare", Decimal("100.00")),
            ("Shopping", Decimal("75.00")),
            ("Insurance", Decimal("200.00")),
            ("Gym", Decimal("50.00")),
            ("Phone Bill", Decimal("65.00")),
            ("Internet", Decimal("60.00")),
            ("Gas", Decimal("50.00")),
            ("Car Maintenance", Decimal("150.00")),
            ("Gifts", Decimal("100.00")),
            ("Books", Decimal("25.00")),
        ]

        # Get all active users
        users = User.objects.filter(status="active")

        if not users.exists():
            self.stdout.write(
                self.style.ERROR("✗ No active users found. Run 'seed_users' first.")
            )
            return

        total_created = 0

        for user in users:
            created_for_user = 0

            # Generate records for the past 6 months
            today = timezone.now().date()
            start_date = today - timedelta(days=180)

            for i in range(record_count):
                # Random date within the 6-month window
                random_days = random.randint(0, 180)
                record_date = start_date + timedelta(days=random_days)

                # 70% expenses, 30% income
                if random.random() < 0.7:
                    record_type = "expense"
                    category, amount = random.choice(expense_categories)
                    # Add some randomness to amounts (±30%)
                    variance = Decimal(random.uniform(0.7, 1.3))
                    amount = amount * variance
                else:
                    record_type = "income"
                    category, amount = random.choice(income_categories)
                    # Add some randomness to amounts (±20%)
                    variance = Decimal(random.uniform(0.8, 1.2))
                    amount = amount * variance

                # Create the record
                record = FinancialRecord.objects.create(
                    user=user,
                    amount=round(amount, 2),
                    record_type=record_type,
                    category=category,
                    date=record_date,
                    notes=f"Sample {record_type} record for {category}",
                )

                created_for_user += 1
                total_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {created_for_user} records for user: {user.username}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Financial records seeding completed! Total records created: {total_created}"
            )
        )

import uuid
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from finance_core.models import RecurringTransaction, User


class Command(BaseCommand):
    help = "Seed recurring transaction data for all users"

    def handle(self, *args, **options):
        # Recurring transaction templates
        recurring_templates = [
            # Income patterns
            {
                "amount": 2000,
                "record_type": "income",
                "category": "Salary",
                "frequency": "monthly",
                "description": "Monthly salary",
                "next_date_offset_days": 14,  # Next payday in 14 days
            },
            {
                "amount": 150,
                "record_type": "income",
                "category": "Freelance",
                "frequency": "weekly",
                "description": "Weekly freelance work",
                "next_date_offset_days": 7,
            },
            # Expense patterns
            {
                "amount": 99,
                "record_type": "expense",
                "category": "Subscriptions",
                "frequency": "monthly",
                "description": "Streaming service subscription",
                "next_date_offset_days": 10,
            },
            {
                "amount": 50,
                "record_type": "expense",
                "category": "Utilities",
                "frequency": "monthly",
                "description": "Internet bill",
                "next_date_offset_days": 5,
            },
            {
                "amount": 30,
                "record_type": "expense",
                "category": "Transportation",
                "frequency": "weekly",
                "description": "Gas",
                "next_date_offset_days": 3,
            },
            {
                "amount": 250,
                "record_type": "expense",
                "category": "Dining",
                "frequency": "weekly",
                "description": "Grocery shopping",
                "next_date_offset_days": 4,
            },
            {
                "amount": 500,
                "record_type": "expense",
                "category": "Insurance",
                "frequency": "quarterly",
                "description": "Car insurance quarterly",
                "next_date_offset_days": 20,
            },
        ]

        users = User.objects.filter(is_active=True)
        created_count = 0

        for user in users:
            self.stdout.write(
                f"\nCreating recurring transactions for user: {user.username}"
            )

            # Helper to add templates based on user role (different patterns for different roles)
            templates_to_use = recurring_templates.copy()

            # Admin users get extra recurring transactions
            if user.role.name == "Admin":
                templates_to_use.extend(
                    [
                        {
                            "amount": 1000,
                            "record_type": "income",
                            "category": "Consulting",
                            "frequency": "biweekly",
                            "description": "Consulting project income",
                            "next_date_offset_days": 8,
                        },
                        {
                            "amount": 200,
                            "record_type": "expense",
                            "category": "Professional Development",
                            "frequency": "monthly",
                            "description": "Course/training subscription",
                            "next_date_offset_days": 12,
                        },
                    ]
                )

            for template in templates_to_use:
                try:
                    # Calculate next_date
                    today = datetime.now().date()
                    next_date = today + timedelta(
                        days=template["next_date_offset_days"]
                    )

                    # Set end_date for some transactions (e.g., subscriptions that might end)
                    end_date = None
                    if (
                        template["record_type"] == "expense"
                        and template["category"] == "Subscriptions"
                    ):
                        end_date = today + timedelta(days=365)  # End in 1 year

                    recurring = RecurringTransaction.objects.create(
                        id=uuid.uuid4(),
                        user=user,
                        amount=template["amount"],
                        record_type=template["record_type"],
                        category=template["category"],
                        frequency=template["frequency"],
                        next_date=next_date,
                        end_date=end_date,
                        description=template["description"],
                        is_active=True,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Created: {template['record_type'].upper()} ${template['amount']} - "
                            f"{template['category']} ({template['frequency']})"
                        )
                    )
                    created_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Error creating recurring transaction: {e}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Recurring transaction seeding complete! Created {created_count} transactions"
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("=" * 60))

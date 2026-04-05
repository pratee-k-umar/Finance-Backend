import uuid

from django.core.management.base import BaseCommand
from finance_core.models import Budget, User


class Command(BaseCommand):
    help = "Seed budget data for all users"

    def handle(self, *args, **options):
        # Budget categories and their limits (monthly)
        budget_templates = [
            {
                "category": "Groceries",
                "limit_amount": 500,
                "frequency": "monthly",
                "alert_at_percentage": 80,
            },
            {
                "category": "Transportation",
                "limit_amount": 300,
                "frequency": "monthly",
                "alert_at_percentage": 75,
            },
            {
                "category": "Entertainment",
                "limit_amount": 200,
                "frequency": "monthly",
                "alert_at_percentage": 85,
            },
            {
                "category": "Utilities",
                "limit_amount": 150,
                "frequency": "monthly",
                "alert_at_percentage": 90,
            },
            {
                "category": "Dining",
                "limit_amount": 400,
                "frequency": "monthly",
                "alert_at_percentage": 80,
            },
        ]

        yearly_budgets = [
            {
                "category": "Vacation",
                "limit_amount": 3000,
                "frequency": "yearly",
                "alert_at_percentage": 70,
            },
            {
                "category": "Insurance",
                "limit_amount": 2000,
                "frequency": "yearly",
                "alert_at_percentage": 95,
            },
        ]

        users = User.objects.filter(is_active=True)
        created_count = 0

        for user in users:
            self.stdout.write(f"\nCreating budgets for user: {user.username}")

            # Create monthly budgets
            for template in budget_templates:
                try:
                    budget, created = Budget.objects.get_or_create(
                        user=user,
                        category=template["category"],
                        frequency=template["frequency"],
                        defaults={
                            "id": uuid.uuid4(),
                            "limit_amount": template["limit_amount"],
                            "alert_at_percentage": template["alert_at_percentage"],
                            "is_active": True,
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Created budget: {template['category']} - "
                                f"${template['limit_amount']}/month (alert at {template['alert_at_percentage']}%)"
                            )
                        )
                        created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error creating budget: {e}")
                    )

            # Create yearly budgets (only for some users to vary data)
            if hash(user.id) % 2 == 0:  # Only for every other user
                for template in yearly_budgets:
                    try:
                        budget, created = Budget.objects.get_or_create(
                            user=user,
                            category=template["category"],
                            frequency=template["frequency"],
                            defaults={
                                "id": uuid.uuid4(),
                                "limit_amount": template["limit_amount"],
                                "alert_at_percentage": template["alert_at_percentage"],
                                "is_active": True,
                            },
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  ✓ Created budget: {template['category']} - "
                                    f"${template['limit_amount']}/year (alert at {template['alert_at_percentage']}%)"
                                )
                            )
                            created_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Error creating budget: {e}")
                        )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Budget seeding complete! Created {created_count} budgets"
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("=" * 60))

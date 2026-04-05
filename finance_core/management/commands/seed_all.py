from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run all seeding commands in sequence"

    def add_arguments(self, parser):
        parser.add_argument(
            "--record-count",
            type=int,
            default=50,
            help="Number of financial records to create per user (default: 50)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # Step 1: Initialize roles
        self.stdout.write(self.style.SUCCESS("\n[1/3] Initializing default roles..."))
        try:
            call_command("init_roles")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error initializing roles: {e}"))
            return

        # Step 2: Seed test users
        self.stdout.write(self.style.SUCCESS("\n[2/3] Seeding test users..."))
        try:
            call_command("seed_users")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error seeding users: {e}"))
            return

        # Step 3: Seed financial records
        record_count = options["record_count"]
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[3/5] Seeding financial records ({record_count} per user)..."
            )
        )
        try:
            call_command("seed_financial_records", count=record_count)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error seeding financial records: {e}")
            )
            return

        # Step 4: Seed budgets
        self.stdout.write(self.style.SUCCESS("\n[4/5] Seeding budgets..."))
        try:
            call_command("seed_budgets")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error seeding budgets: {e}"))
            return

        # Step 5: Seed recurring transactions
        self.stdout.write(
            self.style.SUCCESS("\n[5/5] Seeding recurring transactions...")
        )
        try:
            call_command("seed_recurring_transactions")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error seeding recurring transactions: {e}")
            )
            return

        # Success message
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(
            self.style.SUCCESS("✓ Database seeding completed successfully!")
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # Print login credentials
        self.stdout.write(self.style.WARNING("\nTest User Credentials:"))
        self.stdout.write(self.style.WARNING("-" * 60))

        credentials = [
            ("Viewer", "viewer_user", "viewer123"),
            ("Analyst", "analyst_user", "analyst123"),
            ("Analyst", "analyst_user2", "analyst123"),
            ("Admin", "admin_user", "admin123"),
        ]

        for role, username, password in credentials:
            self.stdout.write(f"  {role:10} | {username:15} | {password}")

        self.stdout.write(self.style.WARNING("-" * 60))
        self.stdout.write("Use these credentials to test API endpoints at:")
        self.stdout.write("  http://localhost:8000/api/v1/")

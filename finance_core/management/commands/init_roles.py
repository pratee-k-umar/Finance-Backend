from django.core.management.base import BaseCommand
from finance_core.models import Role


class Command(BaseCommand):
    help = "Initialize default roles for the finance system"

    def handle(self, *args, **options):
        roles_data = [
            {
                "name": Role.VIEWER,
                "description": "Can only view dashboard data and their own financial records. Cannot create or modify records.",
            },
            {
                "name": Role.ANALYST,
                "description": "Can view and manage their own financial records. Can access detailed analytics.",
            },
            {
                "name": Role.ADMIN,
                "description": "Full system access. Can manage all users, records, and system settings.",
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data["name"],
                defaults={"description": role_data["description"]},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created role: {role.get_name_display()}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"- Role already exists: {role.get_name_display()}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("\n✓ Default roles initialized successfully!")
        )

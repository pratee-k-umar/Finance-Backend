from django.core.management.base import BaseCommand
from finance_core.models import Role, User


class Command(BaseCommand):
    help = "Seed test users with different roles"

    def handle(self, *args, **options):
        users_data = [
            {
                "username": "viewer_user",
                "email": "viewer@example.com",
                "password": "viewer123",
                "first_name": "John",
                "last_name": "Viewer",
                "role_name": Role.VIEWER,
            },
            {
                "username": "analyst_user",
                "email": "analyst@example.com",
                "password": "analyst123",
                "first_name": "Jane",
                "last_name": "Analyst",
                "role_name": Role.ANALYST,
            },
            {
                "username": "analyst_user2",
                "email": "analyst2@example.com",
                "password": "analyst123",
                "first_name": "Bob",
                "last_name": "Smith",
                "role_name": Role.ANALYST,
            },
            {
                "username": "admin_user",
                "email": "admin@example.com",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "role_name": Role.ADMIN,
            },
        ]

        created_count = 0
        existing_count = 0

        for user_data in users_data:
            role_name = user_data.pop("role_name")

            # Get the role
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Role '{role_name}' not found. Run 'init_roles' first."
                    )
                )
                continue

            # Create user if not exists
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "role": role,
                    "status": "active",
                },
            )

            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created user: {user.username} ({role.get_name_display()})"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"- User already exists: {user.username} ({role.get_name_display()})"
                    )
                )
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ User seeding completed! Created: {created_count}, Existing: {existing_count}"
            )
        )

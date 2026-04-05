#!/usr/bin/env python
"""
Sample API usage script demonstrating how to interact with the Finance Backend API
"""

import json
from datetime import datetime, timedelta

import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Session for maintaining cookies
session = requests.Session()


def login(username, password):
    """Authenticate and create session"""
    print(f"Logging in as {username}...")
    response = session.post(
        "http://localhost:8000/api-auth/login/",
        json={"username": username, "password": password},
    )
    if response.status_code == 200:
        print("✓ Login successful\n")
        return True
    else:
        print(f"✗ Login failed: {response.status_code}\n")
        return False


def get_user_profile():
    """Get current user profile"""
    print("Getting user profile...")
    response = session.get(f"{BASE_URL}/users/me/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Current User: {data['username']} ({data['role_name']})\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def get_roles():
    """Get available roles"""
    print("Getting available roles...")
    response = session.get(f"{BASE_URL}/roles/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data)} roles\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def create_financial_record(amount, record_type, category, date, notes=""):
    """Create a financial record"""
    print(f"Creating {record_type} record for ${amount}...")
    payload = {
        "amount": str(amount),
        "record_type": record_type,
        "category": category,
        "date": date,
        "notes": notes,
    }
    response = session.post(f"{BASE_URL}/financial-records/", json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Record created: ID {data['id']}\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Error: {response.json()}\n")
        return None


def get_financial_records(
    category=None, record_type=None, start_date=None, end_date=None
):
    """Get financial records with optional filters"""
    print("Fetching financial records...")
    params = {}
    if category:
        params["category"] = category
    if record_type:
        params["type"] = record_type
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = session.get(f"{BASE_URL}/financial-records/", params=params)
    if response.status_code == 200:
        data = response.json()
        count = data.get("count", len(data.get("results", [])))
        print(f"✓ Found {count} records\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def get_dashboard_summary():
    """Get user's dashboard summary"""
    print("Getting dashboard summary...")
    response = session.get(f"{BASE_URL}/financial-records/summary/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total Income: ${data['total_income']}")
        print(f"  Total Expenses: ${data['total_expenses']}")
        print(f"  Net Balance: ${data['net_balance']}")
        print(f"  Record Count: {data['record_count']}\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def get_category_summary():
    """Get category-wise summary"""
    print("Getting category-wise summary...")
    response = session.get(f"{BASE_URL}/financial-records/category_summary/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Category Breakdown:\n")
        for category in data:
            print(
                f"  {category['category']:20} | Income: ${category['total_income']:10.2f} | "
                f"Expense: ${category['total_expenses']:10.2f} | Net: ${category['net']:10.2f}"
            )
        print()
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def get_monthly_trends(months=6):
    """Get monthly trends"""
    print(f"Getting monthly trends (last {months} months)...")
    response = session.get(
        f"{BASE_URL}/financial-records/monthly_trends/?months={months}"
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Monthly Breakdown:\n")
        for month in data:
            print(
                f"  {month['month']} | Income: ${month['total_income']:10.2f} | "
                f"Expense: ${month['total_expenses']:10.2f} | Net: ${month['net']:10.2f}"
            )
        print()
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def list_users():
    """List all users (Admin only)"""
    print("Fetching all users...")
    response = session.get(f"{BASE_URL}/users/")
    if response.status_code == 200:
        data = response.json()
        count = data.get("count", len(data.get("results", [])))
        print(f"✓ Found {count} users\n")
        return data
    else:
        print(f"✗ Failed: {response.status_code}\n")
        return None


def main():
    """Main demo script"""
    print("=" * 60)
    print("Finance Backend API - Sample Usage Script")
    print("=" * 60 + "\n")

    # 1. Login
    if not login(ADMIN_USERNAME, ADMIN_PASSWORD):
        print("Cannot proceed without authentication")
        return

    # 2. Get user profile
    user = get_user_profile()
    if not user:
        return

    # 3. Get available roles
    roles = get_roles()

    # 4. Create sample financial records
    print("Creating sample financial records...\n")
    today = datetime.now().date()

    records = [
        (5000.00, "income", "Salary", str(today), "Monthly salary"),
        (
            500.00,
            "expense",
            "Groceries",
            str(today - timedelta(days=1)),
            "Weekly shopping",
        ),
        (
            100.00,
            "expense",
            "Utilities",
            str(today - timedelta(days=2)),
            "Electricity bill",
        ),
        (1500.00, "expense", "Rent", str(today - timedelta(days=3)), "Monthly rent"),
    ]

    for amount, type_, category, date_, notes in records:
        create_financial_record(amount, type_, category, date_, notes)

    # 5. Get records
    get_financial_records()

    # 6. Get filtered records
    print("Getting filtered records (Groceries only)...\n")
    get_financial_records(category="Groceries")

    # 7. Get dashboard summary
    get_dashboard_summary()

    # 8. Get category summary
    get_category_summary()

    # 9. Get monthly trends
    get_monthly_trends(months=6)

    # 10. List users (if admin)
    if user["role_name"] == "Admin":
        list_users()

    print("\n" + "=" * 60)
    print("✓ Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API server")
        print("  Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

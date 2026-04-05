#!/usr/bin/env python
"""
Test script for User Management, Role Assignment, and Access Control
Run this script to test all role-based features
"""

import json
import sys
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test credentials
TEST_USERS = {
    "viewer": ("viewer_user", "viewer123", 1),
    "analyst": ("analyst_user", "analyst123", 2),
    "admin": ("admin_user", "admin123", 3),
}

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def log_test(self, name, role, endpoint, method, status_code, expected, success):
        """Log test result"""
        symbol = f"{GREEN}✅{RESET}" if success else f"{RED}❌{RESET}"
        status = (
            f"{GREEN}{status_code}{RESET}" if success else f"{RED}{status_code}{RESET}"
        )

        print(f"{symbol} {name}")
        print(
            f"   Role: {role} | {method} {endpoint} | Status: {status} (expected: {expected})"
        )

        if success:
            self.passed += 1
        else:
            self.failed += 1

    def assert_status(
        self, name, role, endpoint, method, data=None, expected_status=200
    ):
        """Test endpoint and assert status code"""
        username, password, _ = TEST_USERS[role]

        try:
            if method == "GET":
                resp = requests.get(
                    f"{BASE_URL}{endpoint}", auth=(username, password), timeout=5
                )
            elif method == "POST":
                resp = requests.post(
                    f"{BASE_URL}{endpoint}",
                    auth=(username, password),
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
            elif method == "PATCH":
                resp = requests.patch(
                    f"{BASE_URL}{endpoint}",
                    auth=(username, password),
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
            elif method == "DELETE":
                resp = requests.delete(
                    f"{BASE_URL}{endpoint}", auth=(username, password), timeout=5
                )
            else:
                raise ValueError(f"Unknown method: {method}")

            success = resp.status_code == expected_status
            self.log_test(
                name, role, endpoint, method, resp.status_code, expected_status, success
            )
            return success, resp

        except requests.exceptions.ConnectionError:
            print(f"{RED}❌ ERROR: Cannot connect to {BASE_URL}{RESET}")
            print("   Make sure Django is running: python manage.py runserver")
            sys.exit(1)
        except Exception as e:
            print(f"{RED}❌ ERROR: {str(e)}{RESET}")
            return False, None


def print_section(title):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def test_user_listing(runner):
    """Test: List users (Admin only)"""
    print_section("TEST 1: LIST USERS (Admin Only)")

    for role in ["admin", "analyst", "viewer"]:
        expected = 200 if role == "admin" else 403
        runner.assert_status(
            f"{role.capitalize()} lists users",
            role,
            "/users/",
            "GET",
            expected_status=expected,
        )
        print()


def test_create_user(runner):
    """Test: Create user (Admin only)"""
    print_section("TEST 2: CREATE USER (Admin Only)")

    timestamp = int(datetime.now().timestamp())
    payload = {
        "username": f"newuser_{timestamp}",
        "email": f"newuser_{timestamp}@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "TestPass123",
        "password2": "TestPass123",
        "role": 1,
    }

    for role in ["admin", "analyst", "viewer"]:
        expected = 201 if role == "admin" else 403
        runner.assert_status(
            f"{role.capitalize()} creates user",
            role,
            "/users/",
            "POST",
            data=payload,
            expected_status=expected,
        )
        print()


def test_read_records(runner):
    """Test: Read records (All roles)"""
    print_section("TEST 3: READ FINANCIAL RECORDS (All Roles)")

    for role in ["admin", "analyst", "viewer"]:
        runner.assert_status(
            f"{role.capitalize()} reads records",
            role,
            "/financial-records/",
            "GET",
            expected_status=200,
        )
        print()


def test_create_record(runner):
    """Test: Create record (Analyst+)"""
    print_section("TEST 4: CREATE FINANCIAL RECORD (Analyst & Admin)")

    payload = {
        "amount": "123.45",
        "record_type": "expense",
        "category": "Test",
        "date": "2026-04-05",
        "notes": "Test record",
    }

    for role in ["admin", "analyst", "viewer"]:
        expected = 201 if role in ["admin", "analyst"] else 403
        runner.assert_status(
            f"{role.capitalize()} creates record",
            role,
            "/financial-records/",
            "POST",
            data=payload,
            expected_status=expected,
        )
        print()


def test_get_own_profile(runner):
    """Test: Get own profile (All roles)"""
    print_section("TEST 5: GET OWN PROFILE (All Roles)")

    for role in ["admin", "analyst", "viewer"]:
        runner.assert_status(
            f"{role.capitalize()} gets own profile",
            role,
            "/users/me/",
            "GET",
            expected_status=200,
        )
        print()


def test_dashboard_access(runner):
    """Test: Access dashboard (All roles)"""
    print_section("TEST 6: DASHBOARD ACCESS (All Roles)")

    for role in ["admin", "analyst", "viewer"]:
        runner.assert_status(
            f"{role.capitalize()} accesses dashboard summary",
            role,
            "/financial-records/summary/",
            "GET",
            expected_status=200,
        )
        print()


def test_category_summary(runner):
    """Test: Category summary (All roles)"""
    print_section("TEST 7: CATEGORY SUMMARY (All Roles)")

    for role in ["admin", "analyst", "viewer"]:
        runner.assert_status(
            f"{role.capitalize()} views category summary",
            role,
            "/financial-records/category_summary/",
            "GET",
            expected_status=200,
        )
        print()


def test_get_user_details(runner):
    """Test: Get user details"""
    print_section("TEST 8: GET USER DETAILS (Admin Only)")

    # Assuming user ID 1 exists
    for role in ["admin", "analyst", "viewer"]:
        expected = 200 if role == "admin" else 403
        runner.assert_status(
            f"{role.capitalize()} views user details",
            role,
            "/users/1/",
            "GET",
            expected_status=expected,
        )
        print()


def print_summary(runner):
    """Print test summary"""
    total = runner.passed + runner.failed
    print_section("TEST SUMMARY")

    print(f"{GREEN}Passed: {runner.passed}{RESET}")
    print(f"{RED}Failed: {runner.failed}{RESET}")
    print(f"Total:  {total}\n")

    if runner.failed == 0:
        print(f"{GREEN}{'='*60}")
        print(f"✅ ALL TESTS PASSED!".center(60))
        print(f"{'='*60}{RESET}\n")
    else:
        print(f"{RED}{'='*60}")
        print(f"❌ SOME TESTS FAILED".center(60))
        print(f"{'='*60}{RESET}\n")


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print(f"TESTING USERS, ROLES & PERMISSIONS".center(60))
    print(f"{'='*60}{RESET}\n")

    runner = TestRunner()

    try:
        test_user_listing(runner)
        test_create_user(runner)
        test_read_records(runner)
        test_create_record(runner)
        test_get_own_profile(runner)
        test_dashboard_access(runner)
        test_category_summary(runner)
        test_get_user_details(runner)

        print_summary(runner)

        return 0 if runner.failed == 0 else 1

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        return 1
    except Exception as e:
        print(f"\n{RED}Unexpected error: {str(e)}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())

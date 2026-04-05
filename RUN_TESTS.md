# How to Test Users, Roles & Permissions

Complete guide to test all user management, role assignment, and access control features.

---

## Ì∫Ä Quick Start (Choose One)

### Option 1: Python Test Script (Recommended)
```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Run comprehensive test
pip install requests
python test_roles_access.py
```

‚úÖ **Best for:** Comprehensive automated testing with detailed results

---

### Option 2: Bash Quick Test
```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Run quick bash test
bash test_quick.sh
```

‚úÖ **Best for:** Quick manual testing with minimal setup

---

### Option 3: Manual cURL Commands
```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Run individual tests (see examples below)
curl http://localhost:8000/api/users/ -u admin_user:admin123
```

‚úÖ **Best for:** Understanding what's happening step-by-step

---

### Option 4: Django Shell
```bash
python manage.py shell
# Then copy-paste commands from TEST_USERS_AND_ROLES.md section "Test 9"
```

‚úÖ **Best for:** Debugging and database inspection

---

## Ì≥ä What Gets Tested?

### User Management
- ‚úÖ List users (Admin only)
- ‚úÖ Create users (Admin only)
- ‚úÖ Update user status (Admin only)
- ‚úÖ Change user role (Admin only)
- ‚úÖ Delete users (Admin only)
- ‚úÖ Get own profile (All roles)

### Role-Based Access Control
- ‚úÖ Viewer can read but not create
- ‚úÖ Analyst can read and create
- ‚úÖ Admin can do everything
- ‚úÖ Dashboard access for all roles

---

## ÌæØ Pre-Configured Test Users

```
Viewer:   viewer_user  / viewer123  (Role ID: 1)
Analyst:  analyst_user / analyst123 (Role ID: 2)
Admin:    admin_user   / admin123   (Role ID: 3)
```

These users are already created by `seed_all` command.

---

## Ì≥ã Test Files Provided

| File | Purpose | How to Run |
|------|---------|-----------|
| `TEST_USERS_AND_ROLES.md` | Complete test documentation | Read for reference |
| `test_roles_access.py` | Automated Python tests | `python test_roles_access.py` |
| `test_quick.sh` | Quick bash tests | `bash test_quick.sh` |
| `RUN_TESTS.md` | This file | Read for instructions |

---

## Ì¥ç Test Option 1: Python Script (Recommended)

### Setup
```bash
# Install requests library if not already installed
pip install requests
```

### Run
```bash
python test_roles_access.py
```

### Expected Output
```
============================================================
         TESTING USERS, ROLES & PERMISSIONS
============================================================

============================================================
            TEST 1: LIST USERS (Admin Only)
============================================================

‚úÖ Admin lists users
   Role: admin | GET /users/ | Status: 200 (expected: 200)

‚ùå Analyst lists users
   Role: analyst | GET /users/ | Status: 403 (expected: 403)

‚ùå Viewer lists users
   Role: viewer | GET /users/ | Status: 403 (expected: 403)

============================================================
            TEST 2: CREATE USER (Admin Only)
============================================================

‚úÖ Admin creates user
   Role: admin | POST /users/ | Status: 201 (expected: 201)

‚ùå Analyst creates user
   Role: analyst | POST /users/ | Status: 403 (expected: 403)

‚ùå Viewer creates user
   Role: viewer | POST /users/ | Status: 403 (expected: 403)

[... more tests ...]

============================================================
                    TEST SUMMARY
============================================================

Passed: 21
Failed: 0
Total:  21

============================================================
                ‚úÖ ALL TESTS PASSED!
============================================================
```

---

## Ì¥ç Test Option 2: Quick Bash Test

### Run
```bash
bash test_quick.sh
```

### What It Tests
1. Viewer tries to list users (FORBIDDEN)
2. Admin lists users (SUCCESS)
3. Viewer reads financial records (SUCCESS)
4. Viewer tries to create record (FORBIDDEN)
5. Analyst creates financial records (SUCCESS)
6. All roles access dashboard (SUCCESS)

---

## Ì¥ç Test Option 3: Manual cURL Tests

### Test 1: Admin Lists Users ‚úÖ
```bash
curl http://localhost:8000/api/users/ -u admin_user:admin123

# Expected: Status 200 + list of users
```

### Test 2: Analyst Cannot List Users ‚ùå
```bash
curl http://localhost:8000/api/users/ -u analyst_user:analyst123

# Expected: Status 403 + {"detail": "Permission denied"}
```

### Test 3: Viewer Cannot List Users ‚ùå
```bash
curl http://localhost:8000/api/users/ -u viewer_user:viewer123

# Expected: Status 403 + {"detail": "Permission denied"}
```

### Test 4: Admin Creates User ‚úÖ
```bash
curl -X POST http://localhost:8000/api/users/ \
  -u admin_user:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "User",
    "password": "SecurePass123",
    "role": 1
  }'

# Expected: Status 201 + new user data
```

### Test 5: Viewer Cannot Create Record ‚ùå
```bash
curl -X POST http://localhost:8000/api/financial-records/ \
  -u viewer_user:viewer123 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100",
    "record_type": "expense",
    "category": "Test",
    "date": "2026-04-05"
  }'

# Expected: Status 403 + permission denied
```

### Test 6: Analyst Can Create Record ‚úÖ
```bash
curl -X POST http://localhost:8000/api/financial-records/ \
  -u analyst_user:analyst123 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100",
    "record_type": "expense",
    "category": "Test",
    "date": "2026-04-05"
  }'

# Expected: Status 201 + created record
```

### Test 7: All Roles Can Read Records ‚úÖ
```bash
# Viewer
curl http://localhost:8000/api/financial-records/ -u viewer_user:viewer123

# Analyst
curl http://localhost:8000/api/financial-records/ -u analyst_user:analyst123

# Admin
curl http://localhost:8000/api/financial-records/ -u admin_user:admin123

# All Expected: Status 200 + list of records
```

### Test 8: All Roles Can Access Dashboard ‚úÖ
```bash
# Viewer
curl http://localhost:8000/api/dashboard/summary/ -u viewer_user:viewer123

# Analyst
curl http://localhost:8000/api/dashboard/summary/ -u analyst_user:analyst123

# Admin
curl http://localhost:8000/api/dashboard/summary/ -u admin_user:admin123

# All Expected: Status 200 + dashboard data
{
    "total_income": 10000.00,
    "total_expenses": 6000.00,
    "net_balance": 4000.00,
    "record_count": 250,
    "user_count": 5
}
```

---

## Ì¥ç Test Option 4: Django Shell

### Start Shell
```bash
python manage.py shell
```

### List All Users
```python
from finance_core.models import User

users = User.objects.all()
for user in users:
    print(f"{user.username} - Role: {user.role.name} - Status: {user.status}")
```

### Create New User
```python
from finance_core.models import User, Role
from django.contrib.auth.hashers import make_password

new_user = User.objects.create(
    username="test_user",
    email="test@example.com",
    first_name="Test",
    last_name="User",
    role=Role.objects.get(name="viewer"),
    status="active"
)
new_user.set_password("TestPass123")
new_user.save()

print(f"Created: {new_user.username} with role: {new_user.role.name}")
```

### Update User Role
```python
from finance_core.models import User, Role

user = User.objects.get(username="test_user")
user.role = Role.objects.get(name="analyst")
user.save()

print(f"Updated {user.username} role to: {user.role.name}")
```

### Update User Status
```python
from finance_core.models import User

user = User.objects.get(username="test_user")
user.status = "inactive"
user.save()

print(f"Updated {user.username} status to: {user.status}")
```

### List Roles
```python
from finance_core.models import Role

roles = Role.objects.all()
for role in roles:
    print(f"ID: {role.id} - Name: {role.name}")
```

---

## ‚úÖ Expected Test Results

### All Tests Should Show This Pattern:

```
User Management:
‚úÖ Admin can list users (200)
‚ùå Analyst cannot list users (403)
‚ùå Viewer cannot list users (403)

Record Creation:
‚úÖ Admin can create (201)
‚úÖ Analyst can create (201)
‚ùå Viewer cannot create (403)

Dashboard Access:
‚úÖ Admin can access (200)
‚úÖ Analyst can access (200)
‚úÖ Viewer can access (200)
```

---

## Ì∞õ Troubleshooting

### "Connection refused" error
```
Make sure Django is running:
python manage.py runserver
```

### "Permission denied" on all endpoints
```
Check your test credentials:
- Admin: admin_user / admin123
- Analyst: analyst_user / analyst123
- Viewer: viewer_user / viewer123

Or reseed:
python manage.py seed_all
```

### "No module named requests"
```
Install requests:
pip install requests
python test_roles_access.py
```

### Test script permissions error on Windows
```
Run without bash:
python test_roles_access.py

Or use hardcoded curl commands instead
```

---

## Ì≥à Test Coverage Summary

| Feature | Coverage |
|---------|----------|
| Create users | ‚úÖ Admin only |
| Update user status | ‚úÖ Admin only |
| Change user role | ‚úÖ Admin only |
| Delete users | ‚úÖ Admin only |
| List users | ‚úÖ Admin only |
| Get own profile | ‚úÖ All roles |
| Get user details | ‚úÖ Admin only |
| Read records | ‚úÖ All roles |
| Create records | ‚úÖ Analyst & Admin |
| Update records | ‚úÖ Analyst & Admin (own) |
| Delete records | ‚úÖ Analyst & Admin (own) |
| Dashboard access | ‚úÖ All roles |

---

## Ìæì What You'll Learn

After running these tests, you'll verify:

1. **User Management Works**
   - Only admins can create/update/delete users
   - User roles are properly assigned
   - User status can be toggled

2. **Three Roles Function Correctly**
   - **Viewer**: Read-only access
   - **Analyst**: Can create & update own records
   - **Admin**: Full access

3. **Role-Based Access Control Works**
   - Permissions enforced on each endpoint
   - Proper 403 responses for denied access
   - Proper 200/201/204 responses for allowed access

4. **All Users Can Access Shared Features**
   - Dashboard summaries
   - Category breakdowns
   - Monthly trends

---

## Ì≥ö Additional Resources

- `README.md` ‚Äî Full documentation
- `API_GUIDE.md` ‚Äî API endpoint reference
- `TEST_USERS_AND_ROLES.md` ‚Äî Detailed test documentation
- `QUICKSTART.md` ‚Äî Quick command reference

---

**Ready to test? Start with:**
```bash
python test_roles_access.py
```

**Or quick test:**
```bash
bash test_quick.sh
```

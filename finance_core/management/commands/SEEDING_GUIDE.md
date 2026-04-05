# Database Seeding Guide

This directory contains Django management commands to seed your database with test data.

## Available Commands

### 1. **init_roles** (Already Exists)

Initializes the three default system roles:

- **Viewer**: Read-only access to dashboard and personal records
- **Analyst**: Can create/edit own records and view analytics
- **Admin**: Full system access

```bash
python manage.py init_roles
```

### 2. **seed_users**

Creates test users with different roles for testing.

**Test Users Created:**

- `viewer_user` / `viewer123` - Viewer role
- `analyst_user` / `analyst123` - Analyst role
- `analyst_user2` / `analyst123` - Analyst role (second user)
- `admin_user` / `admin123` - Admin role

```bash
python manage.py seed_users
```

### 3. **seed_financial_records**

Generates realistic sample financial records for all active users.

**Features:**

- 50 records per user by default (configurable)
- 70% expenses, 30% income distribution
- Realistic categories and amounts
- Data spread across the past 6 months
- Random variation in amounts (±20-30%)

**Categories Include:**

- **Income**: Salary, Freelance Work, Investment Returns, Bonus, Side Hustle
- **Expenses**: Groceries, Rent, Utilities, Transportation, Dining, Entertainment, Healthcare, Shopping, Insurance, etc.

```bash
# Default: 50 records per user
python manage.py seed_financial_records

# Custom: 100 records per user
python manage.py seed_financial_records --count 100

# Custom: 200 records per user
python manage.py seed_financial_records --count 200
```

### 4. **seed_all** (Master Command - Recommended)

Runs all seeding commands in sequence with proper error handling.

**What It Does:**

1. Initializes default roles
2. Creates test users
3. Seeds financial records (customizable)
4. Displays test credentials for easy reference

```bash
# Default: 50 records per user
python manage.py seed_all

# Custom: 100 records per user
python manage.py seed_all --record-count 100
```

## Quick Start

### Option A: Seed Everything (Recommended)

```bash
python manage.py seed_all
```

### Option B: Seed Step by Step

```bash
python manage.py init_roles
python manage.py seed_users
python manage.py seed_financial_records
```

## Test After Seeding

### 1. Start the server

```bash
python manage.py runserver
```

### 2. Login and test endpoints

#### Get session token (login)

```bash
curl -X POST http://localhost:8000/api-auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst_user", "password": "analyst123"}' \
  -c cookies.txt
```

#### List your financial records

```bash
curl http://localhost:8000/api/v1/financial-records/ \
  -b cookies.txt
```

#### Get dashboard summary

```bash
curl http://localhost:8000/api/v1/financial-records/summary/ \
  -b cookies.txt
```

#### Get category breakdown

```bash
curl http://localhost:8000/api/v1/financial-records/category_summary/ \
  -b cookies.txt
```

#### Get monthly trends

```bash
curl http://localhost:8000/api/v1/financial-records/monthly_trends/ \
  -b cookies.txt
```

## Test User Credentials

After running seed_all, use these credentials:

| Role    | Username      | Password   |
| ------- | ------------- | ---------- |
| Viewer  | viewer_user   | viewer123  |
| Analyst | analyst_user  | analyst123 |
| Analyst | analyst_user2 | analyst123 |
| Admin   | admin_user    | admin123   |

## Data Details

### Financial Record Distribution

- **Time Range**: Past 6 months
- **Records per User**: 50 (default, configurable)
- **Type Distribution**: 70% expenses, 30% income
- **Amount Variation**: ±20-30% randomness for realism

### Sample Data Generated

Each user gets a realistic mix of:

- Regular monthly expenses (rent, utilities, groceries)
- Variable expenses (dining, shopping, entertainment)
- Periodic income (salary, bonuses, side projects)

## Resetting Data

To clear all data and start fresh:

```bash
# Option 1: Delete database and remigrate
rm db.sqlite3
python manage.py migrate
python manage.py seed_all

# Option 2: Clear specific models
python manage.py shell
>>> from finance_core.models import FinancialRecord, User, Role
>>> FinancialRecord.objects.all().delete()
>>> User.objects.all().delete()
>>> Role.objects.all().delete()
>>> exit()
```

## Advanced Usage

### Generate Different Number of Records

```bash
# 200 records per user
python manage.py seed_all --record-count 200

# Just financial records
python manage.py seed_financial_records --count 150
```

### Check Seeded Data

```bash
python manage.py shell
>>> from finance_core.models import User, FinancialRecord
>>> User.objects.count()  # See total users
>>> FinancialRecord.objects.count()  # See total records
>>> user = User.objects.first()
>>> user.financial_records.count()  # Records per user
```

## Troubleshooting

**Issue**: "Role 'analyst' not found"

- **Solution**: Run `python manage.py init_roles` first

**Issue**: "User already exists"

- **Solution**: This is normal - the seed command won't duplicate existing users

**Issue**: "IntegrityError" when seeding

- **Solution**: Reset the database (see "Resetting Data" section above)

---

**Pro Tip**: Save the seeding commands in a shell script for quick setup:

```bash
#!/bin/bash
# setup_dev.sh
python manage.py migrate
python manage.py seed_all
echo "✓ Development environment ready!"
```

Then run: `bash setup_dev.sh`

# Finance Dashboard Backend

A comprehensive Django REST Framework backend for managing financial records, budgets, and transactions with role-based access control, automated scheduling, and email notifications.

**Status:** ✅ Production-Ready | All core requirements + 6 advanced features implemented

---

## Quick Start

```bash
# 1. Setup
cd finance_backend
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Database
python manage.py migrate
python manage.py seed_all

# 3. Run
python manage.py runserver

# Access: http://localhost:8000/api/
# Test users: admin_user/admin123, analyst_user/analyst123, viewer_user/viewer123
```

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Advanced Features](#advanced-features)
- [Celery Scheduler](#celery-scheduler)
- [Email Integration](#email-integration)
- [Docker](#docker-deployment)
- [Troubleshooting](#troubleshooting)

**See `QUICKSTART.md` for quick reference | See `API_GUIDE.md` for detailed API docs**

---

## Features

### Core Requirements ✅

- **User & Role Management** — 3 roles (Viewer, Analyst, Admin) with permissions
- **Financial Records** — CRUD with soft delete, filtering, pagination
- **Dashboard APIs** — Summary, category breakdown, trends
- **Access Control** — Role-based permissions at ViewSet level
- **Validation & Error Handling** — Input validation, meaningful errors
- **Data Persistence** — SQLite ORM with migrations

### Advanced Features ✅

- **Rate Limiting** — 100/hour anon, 1000/hour authenticated
- **Email Notifications** — 4 templates, SMTP configurable
- **Webhooks** — HMAC signing, event logging, retry logic
- **CSV Export** — Records, budgets, recurring transactions
- **Budget Alerts** — Spending tracking, alert thresholds
- **Recurring Transactions** — 6 frequencies, auto-creation via Celery
- **Celery Automation** — Scheduled tasks (midnight, 9 AM)
- **Docker** — Complete containerization

---

## Installation

### Prerequisites
- Python 3.11+
- Redis (optional, for Celery)
- Docker (optional, for containerized deployment)

### Setup

```bash
# Virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Database
python manage.py migrate

# Default roles
python manage.py init_roles

# Test data
python manage.py seed_all
```

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email (see Email Integration section)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@financedashboard.com
```

See `.env.example` for all options.

---

## Running the App

### Development (No Celery)
```bash
python manage.py runserver
```

### With Celery (Automated Tasks)
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A project_settings worker -l info

# Terminal 3: Celery Beat
celery -A project_settings beat -l info

# Terminal 4: Django
python manage.py runserver
```

### Docker (All-in-One)
```bash
docker-compose up -d
docker-compose exec django python manage.py seed_all
```

---

## API Endpoints

### Authentication
```bash
POST /api-auth/login/
POST /api-auth/logout/
```

### Core Endpoints
```
GET/POST    /api/roles/
GET/POST    /api/users/
GET/POST    /api/financial-records/
GET         /api/dashboard/summary/
GET         /api/dashboard/category-summary/
GET         /api/dashboard/monthly-trends/
GET/POST    /api/budgets/
GET/POST    /api/recurring-transactions/
GET/POST    /api/webhooks/
GET/POST    /api/email-notifications/
```

**Query Parameters:**
- `?date_from=2026-01-01` — Filter by start date
- `?date_to=2026-12-31` — Filter by end date
- `?category=Groceries` — Filter by category
- `?record_type=income` — Filter by type
- `?search=salary` — Search records
- `?page=1&page_size=50` — Pagination

**Export to CSV:**
```bash
GET /api/financial-records/export_csv/
GET /api/budgets/export_csv/
GET /api/recurring-transactions/export_csv/
```

See `API_GUIDE.md` for detailed endpoint documentation with examples.

---

## Advanced Features

### Rate Limiting
- **Anonymous:** 100 requests/hour
- **Authenticated:** 1000 requests/hour

### Soft Delete
Records are soft deleted (not removed). Can be recovered by admin:
```bash
DELETE /api/financial-records/{id}/      # Marks deleted
PUT /api/financial-records/{id}/         # Restore
```

### Pagination
```bash
?page=1&page_size=50
```

### Search & Filter
```bash
?search=paycheck&category=Salary&date_from=2026-04-01
```

### CSV Export
```bash
curl http://localhost:8000/api/financial-records/export_csv/ \
  -H "Authorization: Bearer TOKEN" > records.csv
```

---

## Celery Scheduler

Automates recurring transactions and budget checks.

### Setup

```bash
# Install Redis
# Windows: choco install redis-64
# macOS: brew install redis
# Linux: sudo apt-get install redis-server

# Start Redis
redis-server

# Terminal 2: Worker
celery -A project_settings worker -l info

# Terminal 3: Beat
celery -A project_settings beat -l info
```

### Scheduled Tasks

**1. Process Recurring Transactions (Daily at Midnight)**
- Creates financial records from recurring patterns
- Updates next occurrence date
- Manual trigger: `python manage.py process_recurring_transactions`

Example: $2000 salary creates INCOME record every month

**2. Check Budgets & Send Alerts (Daily at 9 AM)**
- Monitors spending vs budget limits
- Creates alerts if threshold exceeded
- Sends email & webhook notifications
- Manual trigger: `python manage.py check_budgets`

Example: Groceries budget $500/month, spent $450 (90%) → Alert sent

### Monitoring

```bash
celery -A project_settings inspect active              # Active tasks
celery -A project_settings inspect scheduled          # Scheduled tasks
celery -A project_settings inspect stats              # Worker stats
pip install flower && celery -A project_settings flower  # UI at :5555
```

---

## Email Integration

Sends notifications for budget alerts, monthly summaries, transactions, and recurring patterns.

### Email Templates
- `budget_alert.html` — Spending threshold alerts
- `monthly_summary.html` — Monthly recap
- `record_created.html` — New transaction notifications
- `recurring_transaction.html` — Auto-transaction alerts

### Setup

**Development (Default - No Setup)**
```bash
# Emails print to console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Production - Gmail SMTP**
```bash
# 1. Enable 2-Factor auth on Google
# 2. Generate App Password at https://myaccount.google.com/apppasswords
# 3. Add to .env:
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

**Production - SendGrid (Recommended)**
```bash
pip install sendgrid-django

# Add to .env:
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.your-api-key
```

### User Preferences
```bash
GET /api/email-notifications/    # View preferences
PUT /api/email-notifications/    # Update preferences
```

Users can disable: budget_alerts, record_created, monthly_summary, recurring_transactions

---

## Docker Deployment

### Quick Start
```bash
docker-compose build
docker-compose up -d
docker-compose exec django python manage.py seed_all
docker-compose ps  # Verify all running
```

### Services
- **Redis** (port 6379) — Celery broker
- **Django** (port 8000) — REST API
- **Celery Worker** — Task executor
- **Celery Beat** — Task scheduler

### Common Commands
```bash
docker-compose logs -f django              # View Django logs
docker-compose logs -f celery-worker       # View worker logs
docker-compose exec django python manage.py shell  # Access shell
docker-compose down                        # Stop all
docker-compose down -v                     # Stop & remove volumes
```

---

## Testing

### Test Role-Based Access
```bash
# Viewer (read-only)
curl http://localhost:8000/api/financial-records/ -u viewer_user:viewer123

# Analyst (read + create)
curl -X POST http://localhost:8000/api/financial-records/ \
  -u analyst_user:analyst123 \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "record_type": "expense", "category": "Test", "date": "2026-04-05"}'

# Admin (full CRUD)
curl -X DELETE http://localhost:8000/api/financial-records/{id}/ \
  -u admin_user:admin123
```

### Test Celery Tasks
```bash
python manage.py shell

from finance_api.tasks import process_recurring_transactions_task
result = process_recurring_transactions_task.delay()
print(result.get())
```

### Test CSV Export
```bash
curl http://localhost:8000/api/financial-records/export_csv/ \
  -H "Authorization: Bearer TOKEN" > records.csv
```

---

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Locked
```bash
docker-compose restart django
```

### Celery Tasks Not Running
```bash
redis-cli ping                                  # Check Redis
celery -A project_settings inspect scheduled   # Check schedule
celery -A project_settings worker -l debug     # Debug worker
```

### Email Not Sending
```bash
python manage.py shell
from django.conf import settings
print(settings.EMAIL_BACKEND)
```

### No Data After Seeding
```bash
python manage.py migrate
python manage.py seed_all --verbosity 3
```

---

## Project Structure

```
finance_backend/
├── project_settings/         # Django configuration
│   ├── settings.py          # Main settings, Celery, Email
│   ├── celery.py            # Celery configuration
│   └── urls.py              # URL routing
│
├── finance_core/            # Core app
│   ├── models.py            # 9 models (User, Budget, etc.)
│   └── management/commands/
│       ├── seed_all.py
│       ├── process_recurring_transactions.py
│       └── check_budgets.py
│
├── finance_api/             # API app
│   ├── views.py             # 8 ViewSets
│   ├── serializers.py       # 15+ serializers
│   ├── permissions.py       # Role-based access
│   ├── utils.py             # Email & webhook utilities
│   ├── tasks.py             # Celery tasks
│   └── csv_export.py        # CSV functions
│
├── templates/emails/        # Email templates
│   ├── budget_alert.html
│   ├── monthly_summary.html
│   ├── record_created.html
│   └── recurring_transaction.html
│
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── README.md               # This file
├── QUICKSTART.md           # Quick reference
└── API_GUIDE.md            # API documentation
```

---

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Django | 4.2.13 | Web framework |
| Django REST Framework | 3.14.0 | API framework |
| Celery | 5.3.4 | Task queue |
| Redis | 5.0.1 | Message broker |
| SQLite | Latest | Database |
| Docker | Latest | Containerization |

---

## Requirements Met

✅ User and Role Management  
✅ Financial Records Management  
✅ Dashboard Summary APIs  
✅ Access Control Logic  
✅ Validation and Error Handling  
✅ Data Persistence  
✅ Rate Limiting  
✅ Email Notifications  
✅ Webhooks  
✅ CSV Export  
✅ Budget Alerts  
✅ Recurring Transactions  
✅ Celery Automation  
✅ Docker Deployment  
✅ Pagination & Search  
✅ Soft Delete  

---

## Next Steps

1. **Start:** `python manage.py runserver`
2. **Access:** `http://localhost:8000/api/`
3. **Login:** `admin_user` / `admin123`
4. **Learn:** Read `QUICKSTART.md` and `API_GUIDE.md`

---

## Documentation

- **QUICKSTART.md** — Quick reference for common tasks
- **API_GUIDE.md** — Detailed API documentation with examples
- **.env.example** — Environment variable options

---

**Mission complete!** ���

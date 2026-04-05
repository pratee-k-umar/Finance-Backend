# Quick Start Guide

## 30-Second Setup

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py seed_all

# Run
python manage.py runserver
```

**Access:** http://localhost:8000/api/

---

## Test Users

```
Admin:    admin_user / admin123
Analyst:  analyst_user / analyst123
Viewer:   viewer_user / viewer123
```

---

## Common Commands

```bash
# Development Server
python manage.py runserver

# Database Operations
python manage.py migrate              # Apply migrations
python manage.py seed_all             # Seed test data
python manage.py shell                # Django shell

# Celery (in separate terminals)
redis-server                          # Start Redis
celery -A project_settings worker    # Start worker
celery -A project_settings beat      # Start scheduler

# Docker
docker-compose up -d                  # Start all services
docker-compose ps                     # Check status
docker-compose logs -f django         # View logs
docker-compose down                   # Stop all
```

---

## API Quick Test

```bash
# View records (Viewer or higher)
curl http://localhost:8000/api/financial-records/ \
  -u admin_user:admin123

# Create record (Analyst or higher)
curl -X POST http://localhost:8000/api/financial-records/ \
  -u analyst_user:analyst123 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "record_type": "expense",
    "category": "Test",
    "date": "2026-04-05"
  }'

# Dashboard summary
curl http://localhost:8000/api/dashboard/summary/ \
  -u admin_user:admin123

# Export CSV
curl http://localhost:8000/api/financial-records/export_csv/ \
  -u admin_user:admin123 > records.csv
```

---

## Configuration

Create `.env`:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## Email Setup

**Development:** Emails print to console (default)

**Gmail:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

**SendGrid:**
```bash
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.your-api-key
```

---

## Celery Tasks

**Manually trigger:**
```bash
python manage.py process_recurring_transactions
python manage.py check_budgets
```

**Scheduled times:**
- Process recurring: Daily at midnight
- Check budgets: Daily at 9 AM

---

## Docker

```bash
# Build & run
docker-compose build
docker-compose up -d

# Seed data
docker-compose exec django python manage.py seed_all

# Access
http://localhost:8000/api/
```

---

## Troubleshooting

**Port in use:**
```bash
python manage.py runserver 8001
```

**Database locked:**
```bash
docker-compose restart django
```

**Celery not running:**
```bash
redis-cli ping  # Should return PONG
```

---

**For detailed docs, see README.md and API_GUIDE.md**

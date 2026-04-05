# API Documentation Guide

## Base URL
```
http://localhost:8000/api/
```

## Authentication

All endpoints require authentication. Use HTTP Basic Auth:
```bash
curl http://localhost:8000/api/endpoint/ -u username:password
```

Or login via session:
```bash
POST /api-auth/login/
{
    "username": "admin_user",
    "password": "admin123"
}
```

---

## Roles & Permissions

| Endpoint | Viewer | Analyst | Admin |
|----------|--------|---------|-------|
| View own records | ✅ | ✅ | ✅ |
| Create records | ❌ | ✅ | ✅ |
| Edit own records | ❌ | ✅ | ✅ |
| Delete own records | ❌ | ✅ | ✅ |
| View all records | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## Roles Endpoint

### List All Roles
```bash
GET /roles/
```

**Response:**
```json
[
    {"id": 1, "name": "viewer", "description": "Can only view dashboard data"},
    {"id": 2, "name": "analyst", "description": "Can view and create records"},
    {"id": 3, "name": "admin", "description": "Full system access"}
]
```

---

## Users Endpoint

### List Users (Admin only)
```bash
GET /users/
```

### Get Current User
```bash
GET /users/me/
```

### Create User (Admin only)
```bash
POST /users/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123",
    "role": 2
}
```

### Update User
```bash
PATCH /users/{id}/
{
    "email": "newemail@example.com",
    "first_name": "Updated"
}
```

### Delete User (Admin only)
```bash
DELETE /users/{id}/
```

---

## Financial Records Endpoint

### List Records
```bash
GET /financial-records/
```

**Query Parameters:**
```bash
?date_from=2026-01-01          # Filter start date
?date_to=2026-12-31             # Filter end date
?category=Groceries             # Filter category
?record_type=income             # Filter type (income/expense)
?search=salary                  # Search in category/notes
?page=1                         # Page number
?page_size=50                   # Items per page
```

**Example:**
```bash
GET /financial-records/?date_from=2026-04-01&category=Groceries&page=1
```

**Response:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/financial-records/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": 1,
            "amount": "500.50",
            "record_type": "expense",
            "category": "Groceries",
            "date": "2026-04-05",
            "notes": "Weekly shopping",
            "is_deleted": false,
            "created_at": "2026-04-05T10:30:00Z",
            "updated_at": "2026-04-05T10:30:00Z"
        }
    ]
}
```

### Get Record
```bash
GET /financial-records/{id}/
```

### Create Record (Analyst+)
```bash
POST /financial-records/
Content-Type: application/json

{
    "amount": "500.50",
    "record_type": "expense",
    "category": "Groceries",
    "date": "2026-04-05",
    "notes": "Weekly shopping"
}
```

### Update Record
```bash
PATCH /financial-records/{id}/
{
    "amount": "600.00",
    "notes": "Updated amount"
}
```

### Delete Record (Soft Delete)
```bash
DELETE /financial-records/{id}/
```

### Export to CSV
```bash
GET /financial-records/export_csv/

# Returns CSV file with columns:
# ID, User, Amount, Type, Category, Date, Notes, Created, Updated
```

---

## Dashboard Endpoints

### Dashboard Summary
```bash
GET /dashboard/summary/?date_from=2026-01-01&date_to=2026-12-31
```

**Response:**
```json
{
    "total_income": 10000.00,
    "total_expenses": 6000.00,
    "net_balance": 4000.00,
    "record_count": 250,
    "user_count": 5
}
```

### Category Summary
```bash
GET /dashboard/category-summary/?date_from=2026-01-01&date_to=2026-12-31
```

**Response:**
```json
[
    {
        "category": "Salary",
        "income": 10000.00,
        "expense": 0.00,
        "net": 10000.00,
        "count": 1
    },
    {
        "category": "Groceries",
        "income": 0.00,
        "expense": 1500.00,
        "net": -1500.00,
        "count": 30
    }
]
```

### Monthly Trends
```bash
GET /dashboard/monthly-trends/?months=12
```

**Response:**
```json
[
    {
        "month": "2026-04",
        "income": 5000.00,
        "expense": 3000.00,
        "net": 2000.00
    },
    {
        "month": "2026-05",
        "income": 5000.00,
        "expense": 3500.00,
        "net": 1500.00
    }
]
```

---

## Budgets Endpoint

### List Budgets
```bash
GET /budgets/
```

### Create Budget
```bash
POST /budgets/
{
    "category": "Groceries",
    "limit_amount": "500.00",
    "frequency": "monthly",
    "alert_at_percentage": 80
}
```

**Frequencies:** `daily`, `weekly`, `monthly`, `quarterly`, `yearly`

### Update Budget
```bash
PATCH /budgets/{id}/
{
    "limit_amount": "600.00",
    "alert_at_percentage": 85
}
```

### Delete Budget
```bash
DELETE /budgets/{id}/
```

### Export Budgets
```bash
GET /budgets/export_csv/
```

---

## Recurring Transactions Endpoint

### List Recurring Transactions
```bash
GET /recurring-transactions/
```

### Create Recurring Transaction
```bash
POST /recurring-transactions/
{
    "category": "Salary",
    "amount": "2000.00",
    "record_type": "income",
    "frequency": "monthly",
    "start_date": "2026-04-05",
    "end_date": "2027-12-31",
    "next_date": "2026-04-05"
}
```

**Frequencies:** `daily`, `weekly`, `biweekly`, `monthly`, `quarterly`, `yearly`

### Update Recurring Transaction
```bash
PATCH /recurring-transactions/{id}/
{
    "amount": "2200.00"
}
```

### Delete Recurring Transaction
```bash
DELETE /recurring-transactions/{id}/
```

### Export to CSV
```bash
GET /recurring-transactions/export_csv/
```

---

## Webhooks Endpoint

### List Webhooks
```bash
GET /webhooks/
```

### Create Webhook
```bash
POST /webhooks/
{
    "url": "https://example.com/webhook",
    "event_type": "record_created",
    "is_active": true,
    "secret": "optional-hmac-secret"
}
```

**Event Types:**
- `record_created` — New financial record
- `record_updated` — Record updated
- `record_deleted` — Record deleted
- `budget_exceeded` — Budget limit exceeded
- `alert_triggered` — Budget alert created

### Update Webhook
```bash
PATCH /webhooks/{id}/
{
    "is_active": false
}
```

### Delete Webhook
```bash
DELETE /webhooks/{id}/
```

### Test Webhook
```bash
POST /webhooks/{id}/test/

# Sends test payload to webhook URL
```

### List Webhook Events
```bash
GET /webhooks/{id}/events/

# Returns all events fired for this webhook
```

---

## Email Notifications Endpoint

### Get Email Preferences
```bash
GET /email-notifications/
```

**Response:**
```json
{
    "budget_alerts": true,
    "record_created": false,
    "monthly_summary": true,
    "recurring_transactions": true
}
```

### Update Email Preferences
```bash
PUT /email-notifications/
{
    "budget_alerts": true,
    "record_created": true,
    "monthly_summary": false,
    "recurring_transactions": true
}
```

---

## Budget Alerts Endpoint

### List Budget Alerts
```bash
GET /budget-alerts/
```

### Get Alert Details
```bash
GET /budget-alerts/{id}/
```

### Mark Alert as Dismissed
```bash
POST /budget-alerts/{id}/dismiss/
```

---

## Error Handling

### Error Response Format
```json
{
    "detail": "Error message",
    "status_code": 400
}
```

### Common Status Codes
- **200 OK** — Success
- **201 Created** — Resource created
- **204 No Content** — Delete successful
- **400 Bad Request** — Validation error
- **401 Unauthorized** — Not authenticated
- **403 Forbidden** — Permission denied
- **404 Not Found** — Resource not found
- **429 Too Many Requests** — Rate limit exceeded
- **500 Server Error** — Server error

---

## Rate Limiting

Response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1680000000
```

**Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour

---

## Examples with cURL

### Create Record
```bash
curl -X POST http://localhost:8000/api/financial-records/ \
  -u admin_user:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "record_type": "expense",
    "category": "Groceries",
    "date": "2026-04-05",
    "notes": "Weekly shopping"
  }'
```

### List Records with Filters
```bash
curl "http://localhost:8000/api/financial-records/?category=Salary&record_type=income&date_from=2026-04-01" \
  -u admin_user:admin123
```

### Get Dashboard Summary
```bash
curl http://localhost:8000/api/dashboard/summary/ \
  -u admin_user:admin123
```

### Create Budget
```bash
curl -X POST http://localhost:8000/api/budgets/ \
  -u admin_user:admin123 \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Groceries",
    "limit_amount": "500",
    "frequency": "monthly",
    "alert_at_percentage": 80
  }'
```

### Export CSV
```bash
curl http://localhost:8000/api/financial-records/export_csv/ \
  -u admin_user:admin123 > records.csv
```

---

## Webhook Payload Example

```json
{
    "event_type": "record_created",
    "timestamp": "2026-04-05T10:30:00Z",
    "data": {
        "id": 1,
        "user": 1,
        "amount": "500.50",
        "record_type": "expense",
        "category": "Groceries",
        "date": "2026-04-05",
        "notes": "Weekly shopping",
        "created_at": "2026-04-05T10:30:00Z"
    }
}
```

**HMAC Header:**
```
X-Webhook-Signature: sha256=HMAC_HASH_VALUE
```

---

For more information, see [README.md](README.md)

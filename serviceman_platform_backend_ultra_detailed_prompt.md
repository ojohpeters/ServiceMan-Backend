# Serviceman Platform Backend — ULTRA-DETAILED IMPLEMENTATION PROMPT

You are an expert Django backend engineer. Build a **fully production-ready Django REST API** for the Serviceman three-sided marketplace, strictly following the specifications below. Every word is an implementation requirement.

---

## 1. PROJECT OVERVIEW

**Platform Purpose:**  
A three-sided marketplace connecting **Clients** (who book/pay/approve services), **Servicemen** (who accept, estimate, and complete jobs), and **Admins** (who control workflow and finances) for on-demand service booking, emergency jobs, price negotiation, and dual-channel notifications.

---

## 2. PROJECT STRUCTURE

**You MUST use this exact structure:**
```
serviceman_backend/
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── tests/
│   │   └── urls.py
│   ├── services/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tests/
│   │   └── urls.py
│   ├── payments/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── paystack.py
│   │   ├── tests/
│   │   └── urls.py
│   ├── negotiations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tests/
│   │   └── urls.py
│   ├── notifications/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   └── templates/emails/
│   └── ratings/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── tests/
│       └── urls.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── .env.example
├── .gitignore
├── manage.py
├── pytest.ini
└── README.md
```

---

## 3. DEPENDENCIES

**Pin exact versions in `requirements/base.txt`:**
```
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-environ==0.11.2
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0
django-cors-headers==4.3.1
drf-spectacular==0.27.0
django-ratelimit==4.1.0
Pillow==10.1.0
gunicorn==21.2.0
whitenoise==6.6.0
sentry-sdk==1.38.0
pytest==7.4.3
pytest-django==4.7.0
factory-boy==3.3.0
faker==20.1.0
requests==2.31.0
```

---

## 4. CONFIGURATION & ENVIRONMENT

- Use `django-environ` to manage all secrets.
- `.env.example` must include all: SECRET_KEY, DEBUG, DB, EMAIL, PAYSTACK, REDIS, CORS, SENTRY, etc.
- Never commit `.env` to git.
- Configure `config/settings/production.py` for:
    - `DEBUG = False`
    - `SECRET_KEY` from env
    - `ALLOWED_HOSTS` from env
    - PostgreSQL, Gunicorn, WhiteNoise/S3, Redis, Sentry, CORS whitelist
    - `SECURE_SSL_REDIRECT = True`
- Use PostgreSQL.
- Set up Celery with Redis.
- Use Django's default PBKDF2 password hash.

---

## 5. USER & AUTH MODULE

### Models (`apps/users/models.py`)

#### User (custom):
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'ADMIN'
    SERVICEMAN = 'SERVICEMAN'
    CLIENT = 'CLIENT'
    USER_TYPE_CHOICES = [
        (ADMIN, 'Admin'),
        (SERVICEMAN, 'Serviceman'),
        (CLIENT, 'Client'),
    ]
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    REQUIRED_FIELDS = ['email', 'user_type']

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ServicemanProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='serviceman_profile')
    category = models.ForeignKey('services.Category', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_jobs_completed = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Permissions (`apps/users/permissions.py`)

```python
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'ADMIN'

class IsServiceman(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'SERVICEMAN'

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'CLIENT'
```

### Authentication

- Use JWT (djangorestframework-simplejwt).
- Endpoints:
    - `POST /api/auth/register/` (register new user, send email verification)
    - `POST /api/auth/login/` (get JWT)
    - `POST /api/auth/refresh/` (refresh token)
    - `POST /api/auth/verify-email/` (token-based)
    - `POST /api/auth/forgot-password/` (send reset email)
    - `POST /api/auth/reset-password/` (set new password)
- Passwords: min 8 chars, uppercase, lowercase, number.
- Require email verification before booking.
- Rate limit auth endpoints (5/min).
- Custom JWT payload to include user_type.
- Test all edge cases.

---

## 6. CATEGORY & SERVICEMAN DIRECTORY

### Models (`apps/services/models.py`)

#### Category
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

- List endpoint (`GET /api/categories/`) shows only active categories.
- List servicemen in category (`GET /api/categories/{id}/servicemen/`) includes name, rating, total jobs, bio, years of experience.
- Admin can create/update categories.

---

## 7. BOOKING WORKFLOW (SERVICE REQUEST)

### Models (`apps/services/models.py`)

#### ServiceRequest
```python
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING_ADMIN_ASSIGNMENT', ...),
        ('ASSIGNED_TO_SERVICEMAN', ...),
        ('SERVICEMAN_INSPECTED', ...),
        ('AWAITING_CLIENT_APPROVAL', ...),
        ('NEGOTIATING', ...),
        ('AWAITING_PAYMENT', ...),
        ('PAYMENT_CONFIRMED', ...),
        ('IN_PROGRESS', ...),
        ('COMPLETED', ...),
        ('CANCELLED', ...),
    ]
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='client_requests')
    serviceman = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='serviceman_requests')
    backup_serviceman = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='backup_requests')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    booking_date = models.DateField()
    is_emergency = models.BooleanField(default=False)
    auto_flagged_emergency = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    initial_booking_fee = models.DecimalField(max_digits=10, decimal_places=2)
    serviceman_estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client_address = models.TextField()
    service_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inspection_completed_at = models.DateTimeField(null=True, blank=True)
    work_completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
```

- Auto-set `is_emergency` and `auto_flagged_emergency` if booking date < today+2.
- Only client, assigned serviceman, backup, or admin can access a request.
- Soft delete via `is_deleted`.

---

## 8. PAYMENT (PAYSTACK)

### Models (`apps/payments/models.py`)

```python
from django.db.models import JSONField

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('INITIAL_BOOKING', ...),
        ('FINAL_PAYMENT', ...),
    ]
    STATUS_CHOICES = [
        ('PENDING', ...),
        ('SUCCESSFUL', ...),
        ('FAILED', ...),
    ]
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=16, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=100, unique=True)
    paystack_access_code = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    metadata = JSONField(default=dict)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

- Use environment variables: PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY, PAYSTACK_WEBHOOK_SECRET.
- No hardcoded keys.
- Implement endpoints:
    - `POST /api/payments/initialize/` — return Paystack checkout URL after creating Payment record.
    - `POST /api/payments/webhook/` — verify signature, update payment, trigger workflow.
    - `GET /api/payments/verify/{reference}/`
- Validate payment amount matches.
- Prevent duplicate payment processing.

---

## 9. NOTIFICATIONS (DUAL CHANNEL)

- Model (`apps/notifications/models.py`):
    - user, notification_type, title, message, service_request (nullable FK), is_read, sent_to_email, email_sent_at, created_at
- **Every notification must be sent to both:**
    1. Dashboard (Notification instance, API endpoint to list)
    2. Email (via Celery async task, render HTML template)
- Email templates for every notification type.
- Endpoints:
    - `GET /api/notifications/`
    - `PATCH /api/notifications/{id}/read/`
    - `PATCH /api/notifications/mark-all-read/`
    - `GET /api/notifications/unread-count/`
- Real-time (Django Channels) is optional but recommended.

**Critical Notification Triggers** (all dual-channel):
- Payment received → Admin
- Serviceman assigned → Serviceman + backup
- Cost estimate ready → Admin
- Final cost set → Client
- Negotiation message → Admin/Client
- Payment confirmed → Admin + Serviceman
- Job completed → Admin
- Job confirmed complete → Client
- Emergency flag added/changed → Serviceman

- Use Celery for all email sending. Never block API on email.
- All notification creation must be tested.

---

## 10. NEGOTIATION SYSTEM

### Models (`apps/negotiations/models.py`)

```python
class PriceNegotiation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', ...),
        ('ACCEPTED', ...),
        ('REJECTED', ...),
        ('COUNTERED', ...),
    ]
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.CASCADE)
    proposed_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    parent_negotiation = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
```

- Only client and admin may propose/counter/accept/reject.
- Serviceman is consulted but not a direct participant.
- Endpoints:
    - `POST /api/negotiations/` — propose price
    - `POST /api/negotiations/{id}/respond/` — accept/reject/counter
    - `GET /api/negotiations/?request_id=X`
    - `POST /api/negotiations/{id}/check-with-serviceman/`
- All negotiation messages stored for audit trail.

---

## 11. RATING SYSTEM

### Models (`apps/ratings/models.py`)

```python
class Rating(models.Model):
    service_request = models.OneToOneField('services.ServiceRequest', on_delete=models.CASCADE)
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="ratings_given")
    serviceman = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="ratings_received")
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

- After job completion, client rates serviceman (1-5), leaves review.
- Update serviceman's running average and total_jobs_completed.
- Endpoints:
    - `POST /api/ratings/`
    - `GET /api/ratings/?serviceman_id=X`

---

## 12. ADMIN DASHBOARD & ANALYTICS

- Endpoints:
    - `GET /api/admin/pending-assignments/`
    - `POST /api/admin/assign-serviceman/`
    - `GET /api/admin/pricing-review/`
    - `PATCH /api/admin/update-final-cost/`
    - `GET /api/admin/analytics/revenue/`
    - `GET /api/admin/analytics/servicemen/`
    - `GET /api/admin/analytics/categories/`
- Must return all relevant job, payment, negotiation, and rating data.
- Admin actions: assign servicemen, set markups, respond to negotiations, verify completion, manage categories/users.

---

## 13. STATUS PROGRESSION

**Implement status transitions exactly as follows:**
```
1. PENDING_ADMIN_ASSIGNMENT (after payment confirmed)
   ↓
2. ASSIGNED_TO_SERVICEMAN (admin assigns)
   ↓
3. SERVICEMAN_INSPECTED (serviceman submits estimate)
   ↓
4. AWAITING_CLIENT_APPROVAL (admin sets final cost)
   ↓
5a. NEGOTIATING (if client negotiates) → back to step 4
   OR
5b. AWAITING_PAYMENT (client agrees to price)
   ↓
6. PAYMENT_CONFIRMED (client pays final amount)
   ↓
7. IN_PROGRESS (serviceman working)
   ↓
8. COMPLETED (serviceman marks complete, admin verifies)

Alternative flows:
- CANCELLED (client or admin cancels at any stage)
- REASSIGNED (if serviceman declines, goes to backup)
```
- Every status transition must be enforced by permissions and validated in tests.

---

## 14. TESTING

- **Unit tests:** All models (validation/methods), all serializers, all utility functions (emergency logic, markup calculation).
- **Integration tests:** Complete booking workflow, payment verification, negotiation, notification (both channels), all status transitions.
- **API tests:** All endpoints (success, auth, permission, error, edge cases).
- **Coverage:** Minimum 80%. Use `pytest`, `pytest-django`, `factory_boy`, `faker`. Mock Paystack and email.
- **Test that every notification triggers both dashboard and email.**

---

## 15. CELERY TASKS

**Implement these Celery tasks:**
- `send_notification_email(notification_id)`
- `send_bulk_notifications(user_ids, notification_data)`
- `verify_payment_status(payment_id)`
- `check_overdue_inspections()` (servicemen not inspecting after 24hrs)
- `update_serviceman_ratings()`
- `generate_revenue_report(period)`
- Use Redis as broker, result backend, retry with exponential backoff, monitor with Flower.

---

## 16. DEPLOYMENT

- Gunicorn as WSGI, Nginx reverse proxy, SSL (Let's Encrypt), WhiteNoise/S3 for static.
- Sentry for error monitoring.
- Django logging for all errors/warnings.
- Celery Flower for monitoring.
- CI/CD with tests before deploy, environment variable validation, database migration check.

---

## 17. EMAIL TEMPLATES

**Implement HTML templates for:**
1. Welcome Email
2. Email Verification
3. Booking Confirmation
4. Serviceman Assignment
5. Backup Opportunity
6. Cost Estimate Ready
7. Final Cost Set
8. Negotiation Message
9. Payment Received
10. Job Completed
11. Emergency Alert

---

## 18.
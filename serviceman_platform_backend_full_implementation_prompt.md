# Serviceman Platform Backend — COMPLETE Implementation Prompt

You are an expert Django backend engineer. Build a **production-ready Django REST API backend** for a three-sided marketplace connecting **Clients**, **Servicemen**, and **Admins** for on-demand service booking, negotiation, and dual-channel notifications.

---

## SYSTEM GOALS

- Three roles: **Client**, **Serviceman**, **Admin**.
- Complete booking workflow (see below).
- DUAL-CHANNEL notifications (dashboard + email) for every critical event.
- Secure, environment-variable-only Paystack integration.
- Emergency service auto-detection & logic.
- Role-based permissions at every level.
- Full test coverage, OpenAPI docs, and production-grade settings.

---

## 1. BOOKING WORKFLOW

**Implement the following booking flow, step by step:**

### (1) Client Browsing & Booking

- Expose endpoints:
    - List all active categories.
    - List all servicemen in a category, with name, rating, jobs completed, bio, years of experience.
- Client views serviceman profile and selects "Book".
- Client selects booking date.

### (2) Emergency Detection & Pricing

- If booking_date < today + 2 days: auto-flag as emergency (set `auto_flagged_emergency` = True).
- Client can manually toggle emergency flag (but cannot unset if auto-flag logic triggers).
- Booking fee:
    - Emergency: ₦5,000
    - Non-emergency: ₦2,000
- Booking fee is set and returned from backend with emergency flag status.

### (3) Payment (Paystack Integration)

- `POST /api/payments/initialize/` — Initialize Paystack payment for booking fee, return checkout URL.
- Store all payment attempts in a Payment model:
    - service_request, payment_type, amount, paystack_reference, paystack_access_code, status, paid_at, metadata (store client info as JSON).
- After payment, only proceed if webhook is received & signature verified.
- Expose webhook endpoint (`POST /api/payments/webhook/`) and manual verify endpoint (`GET /api/payments/verify/{reference}/`).
- Block duplicate processing.

### (4) Admin Assignment

- After payment, create ServiceRequest with status = PENDING_ADMIN_ASSIGNMENT.
- Expose admin endpoint showing unassigned requests with all client/serviceman/category/emergency details.
- Admin assigns both primary and backup serviceman, can set/override emergency flag.
- Assignment triggers dual-channel notification to both primary and backup serviceman.

### (5) Serviceman Notification (Dual Channel)

- On assignment, both primary and backup serviceman receive notification:
    - Dashboard (API endpoint for notifications)
    - Email (async via Celery)
- Notification includes client details, service description, booking date, and emergency status (highlighted if True).

### (6) Cost Estimation

- Serviceman inspects client site (offline).
- Serviceman submits estimate via `POST /api/serviceman/submit-estimate/` (amount, notes).
- Status transitions to SERVICEMAN_INSPECTED. Dual-channel notification to admin.

### (7) Admin Markup

- Admin reviews estimate, sets markup %, calculates final cost, sets status to AWAITING_CLIENT_APPROVAL or NEGOTIATING.
- Dual-channel notification to client with new cost.

### (8) Negotiation (Optional)

- Client can counter-offer (enter price + message).
- Admin receives notification, can accept/counter/ask serviceman if acceptable.
- Negotiation is tracked in a model (`PriceNegotiation`), all messages and offers are stored.
- Once agreement is reached, status moves to AWAITING_PAYMENT.

### (9) Final Payment

- Client pays final cost via Paystack.
- Webhook or manual verification confirms payment, updates status to PAYMENT_CONFIRMED.
- Dual-channel notification to admin + serviceman.

### (10) Work Execution

- Admin notifies serviceman to proceed (dashboard + email).
- Serviceman does work offline, then marks job as complete via API.

### (11) Completion & Rating

- Admin verifies with client, marks job as completed.
- Client receives notification.
- Client rates serviceman (1-5 stars), can leave a review. Updates running average on ServicemanProfile, increments job count.

---

## 2. DUAL-CHANNEL NOTIFICATIONS

**Every notification must be sent to both:**
- Dashboard (Notification model, retrievable via API)
- Email (async via Celery, with customizable templates per notification type)

**Notification triggers include:**
- Payment received → Admin
- Serviceman assigned → Serviceman + backup
- Cost estimate ready → Admin
- Final cost set → Client
- Negotiation message → Admin/Client
- Payment confirmed → Admin + Serviceman
- Job completed → Admin
- Job confirmed complete → Client
- Emergency flag added/changed → Serviceman

**Notification Model:**
- user (FK)
- notification_type (str)
- title
- message
- service_request (nullable FK)
- is_read (bool)
- sent_to_email (bool)
- email_sent_at (datetime)
- created_at

**Endpoints:**
- List (paginated)
- Mark as read
- Mark all as read
- Unread count

---

## 3. PAYSTACK INTEGRATION

- Use only PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY, PAYSTACK_WEBHOOK_SECRET from env
- Payment model as above (see booking flow)
- Signature-verified webhook endpoint for payment confirmation
- Manual payment verify endpoint
- Validate amounts and statuses on every payment event
- Never process the same payment twice

---

## 4. EMERGENCY LOGIC

- If booking date < today + 2 days → auto-flag emergency (client cannot unset)
- Booking fee = 5000 if emergency, else 2000
- Emergency flag is always stored for every ServiceRequest
- Emergency flag is passed through all notification payloads

---

## 5. NEGOTIATION SYSTEM

- `PriceNegotiation` model:
    - service_request (FK)
    - proposed_by (FK to User)
    - proposed_amount
    - message
    - status (PENDING, ACCEPTED, REJECTED, COUNTERED)
    - created_at
- Endpoints:
    - Propose price
    - Accept proposal
    - Counter proposal
    - List negotiation history per service request

---

## 6. RATING SYSTEM

- `Rating` model:
    - service_request (OneToOne)
    - rating (int, 1-5)
    - review (text)
    - created_at
- After job completion, client can rate serviceman and leave review
- Serviceman profile updates: running average, job count

---

## 7. ADMIN ANALYTICS

- Endpoints:
    - Revenue summary
    - Top servicemen by rating/jobs
    - Most requested categories

---

## 8. SECURITY & TESTING

- All sensitive config in `.env` (never hardcoded)
- Use Django PBKDF2 password hashing
- JWT authentication (djangorestframework-simplejwt)
- Role-based DRF permissions (IsAdmin, IsServiceman, IsClient, etc.)
- CSRF enabled on session endpoints
- CORS with whitelist
- Rate limiting on auth/payment endpoints
- Strict input validation via DRF serializers
- No raw SQL, only ORM
- Logging and error handling in all critical flows
- Soft delete (is_deleted, deleted_at) on ServiceRequest
- Minimum 80% code coverage on all tests (pytest, factory_boy, faker)

---

## 9. DEPLOYMENT

- PostgreSQL as DB
- Celery with Redis for async tasks
- Gunicorn/uWSGI with Nginx
- Static files via WhiteNoise or S3
- LetsEncrypt SSL
- Sentry for error monitoring
- Automated DB backups

---

## 10. CODE STRUCTURE

```
serviceman_project/
├── apps/
│   ├── users/
│   ├── services/
│   ├── payments/
│   ├── negotiations/
│   ├── notifications/
│   └── ratings/
├── config/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── requirements/
├── .env.example
├── manage.py
└── README.md
```

---

## 11. DOCUMENTATION

- Use drf-spectacular for OpenAPI docs.
- Document all endpoints (request/response, permissions, errors).
- Include API examples for all key flows.

---

**Build this backend to exactly match the requirements above, with production-ready, fully tested, and documented code.**
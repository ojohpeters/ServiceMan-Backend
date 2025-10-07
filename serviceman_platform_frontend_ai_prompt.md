# Serviceman Platform Frontend — Complete AI Implementation Prompt

You are an expert AI frontend developer. Using the backend API **exactly as described below** (reflecting the backend implementation), build a fully production-ready, modern, responsive frontend for the Serviceman Platform — a three-sided marketplace for Clients, Servicemen, and Admins.

---

## 1. TECH STACK & PROJECT SETUP

- **React** (v18+) with **TypeScript**
- **Next.js** (v13+) or **Vite**
- **Redux Toolkit** for global state
- **React Query** for data fetching/caching
- **Tailwind CSS** for styling
- **Formik + Yup** for forms and validation
- **WebSocket** or **socket.io-client** for real-time notifications (or poll every 30s as fallback)
- **Paystack JS SDK** for payments (public key from env)
- Store JWTs in httpOnly cookies (preferred) or encrypted localStorage
- Use environment variables for API base URL, Paystack public key, etc.
- Ready for Vercel/Netlify deployment

---

## 2. ROUTING & LAYOUT

| Path                                 | Who         | Description                                      |
|---------------------------------------|-------------|--------------------------------------------------|
| `/`                                  | All         | Landing page, features, CTA                      |
| `/login`, `/register`                 | All         | Auth flows (JWT)                                 |
| `/forgot-password`, `/reset-password` | All         | Password reset flow                              |
| `/verify-email`                       | All         | Email verification (token from URL)              |
| `/dashboard`                          | All         | Role-based dashboard: redirects to correct area  |
| `/categories`                         | All         | List all active categories                       |
| `/categories/[id]`                    | All         | List servicemen in category                      |
| `/servicemen/[id]`                    | All         | Serviceman public profile                        |
| `/service-requests/[id]`              | All         | Service request details (role-based)             |
| `/notifications`                      | All         | List of notifications, mark as read              |
| `/admin`                              | Admin       | Admin dashboard                                  |
| `/admin/assignments`                  | Admin       | Pending assignments                              |
| `/admin/pricing`                      | Admin       | Cost estimates, markup                           |
| `/admin/negotiations`                 | Admin       | Negotiation threads                              |
| `/admin/analytics`                    | Admin       | Revenue, categories, servicemen analytics        |
| `/admin/users`                        | Admin       | User management                                  |
| `/admin/categories`                   | Admin       | Category management                              |
| `/negotiations/[requestId]`           | Client/Admin| Negotiation chat view                            |

---

## 3. AUTHENTICATION & SECURITY

- Register/Login via **JWT** (`/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/`)
- Store JWT in httpOnly cookie if possible
- Require email verification before booking: `/api/auth/verify-email/`
- Password: min 8 chars, uppercase, lowercase, number (validate with Yup)
- On 401/403, auto logout and redirect to `/login`
- Rate limit login attempts UI to 5/min

---

## 4. CLIENT FLOWS

### Booking

- Browse categories: `GET /api/categories/`
- View servicemen: `GET /api/categories/{id}/servicemen/`
- View profile: `GET /api/servicemen/{id}/` (or from above)
- Book: Select serviceman, choose date, toggle emergency (auto-flag if date ≤ 2 days out)
- Calculate initial fee: ₦5,000 (emergency) or ₦2,000 (normal)
- Submit booking: `POST /api/service-requests/` (fields: serviceman_id, category_id, booking_date, is_emergency, address, description)
- After booking, show payment page:
    - Initialize payment: `POST /api/payments/initialize/`
    - Redirect to Paystack checkout URL
    - After payment, show "Pending Admin Assignment" status
- Track all requests: `GET /api/service-requests/` (filtered by user)
- View request: `GET /api/service-requests/{id}/`
- If negotiation open, show chat UI (see Negotiations)
- If final payment needed, show Paystack button
- After job completed, prompt for rating: `POST /api/ratings/`

### Notifications

- Unread count: `GET /api/notifications/unread-count/`
- List: `GET /api/notifications/`
- Mark as read: `PATCH /api/notifications/{id}/read/`
- Mark all as read: `PATCH /api/notifications/mark-all-read/`
- Real-time updates via WebSocket/poll

---

## 5. SERVICEMAN FLOWS

### Dashboard

- Assigned jobs: `GET /api/serviceman/assigned-jobs/`
- Accept/decline: `POST /api/serviceman/accept-job/{id}/` or `POST /api/serviceman/decline-job/{id}/`
- Submit estimate: `POST /api/serviceman/submit-estimate/` (request_id, estimated_cost, notes)
- Mark job complete: `POST /api/serviceman/complete-job/{id}/`
- Earnings: `GET /api/serviceman/earnings/`
- Update profile: `PATCH /api/serviceman-profile/`
- See ratings

### Notifications

- Assignment, backup, payment, markup, job complete, all via dashboard and email
- Real-time updates

---

## 6. ADMIN FLOWS

### Dashboard

- Pending assignments: `GET /api/admin/pending-assignments/`
- Assign serviceman: `POST /api/admin/assign-serviceman/` (request_id, serviceman_id, backup_serviceman_id, is_emergency)
- Pricing review: `GET /api/admin/pricing-review/`
- Set final cost: `PATCH /api/admin/update-final-cost/` (request_id, serviceman_cost, markup_percentage, final_cost)
- Negotiations: `GET /api/negotiations/?request_id=X`, respond/counter via `POST /api/negotiations/{id}/respond/`
- Analytics:
    - Revenue: `GET /api/admin/analytics/revenue/`
    - By servicemen: `GET /api/admin/analytics/servicemen/`
    - By categories: `GET /api/admin/analytics/categories/`
- Manage categories: `GET/POST/PATCH /api/categories/`
- Manage users: (custom as needed)

---

## 7. NEGOTIATION UI

- Chat-style: `GET /api/negotiations/?request_id=X`
- Start: `POST /api/negotiations/` (service_request, proposed_amount, message)
- Respond: `POST /api/negotiations/{id}/respond/` (accept/reject/counter)
- Show status: pending/accepted/countered/rejected
- If admin, can "Check with Serviceman": `POST /api/negotiations/{id}/check-with-serviceman/`

---

## 8. PAYMENTS

- Use Paystack JS SDK and public key from env
- Initialize: `POST /api/payments/initialize/` (service_request, payment_type, amount)
- Webhook/verification handled by backend; frontend only needs to redirect and display status
- Show payment history for each request

---

## 9. NOTIFICATIONS

- All critical actions must show notification in dashboard and (simulate) email
- Real-time dashboard updates via WebSocket (or poll)
- Mark as read, mark all as read
- Unread badge on bell icon

---

## 10. EMAIL FLOWS

- Simulate/resend all backend-triggered emails (welcome, verification, assignment, backup, estimate, markup, negotiation, payment, job complete, emergency)
- "Resend" button for email if user didn’t receive

---

## 11. SECURITY & VALIDATION

- All forms use Formik+Yup, match backend field rules
- No admin actions exposed to non-admins
- All critical actions require confirmation dialog
- Paystack secret keys never exposed in frontend
- All API calls via HTTPS
- CORS origin must match backend whitelist

---

## 12. RESPONSIVE DESIGN

- 100% responsive: mobile, tablet, desktop
- Tailwind grid/flex for layouts

---

## 13. TESTING

- Use Jest + React Testing Library
- Test all critical flows: booking, payment, negotiation, notifications
- Minimum 80% coverage

---

## 14. DEPLOYMENT

- Ready for Vercel/Netlify
- `.env.example` with all needed variables (API URL, Paystack public key)
- `README.md` with setup, build, deploy steps

---

## 15. API ENDPOINTS OVERVIEW (MUST MATCH BACKEND)

### Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/verify-email/`
- `POST /api/auth/forgot-password/`
- `POST /api/auth/reset-password/`

### Categories
- `GET /api/categories/`
- `GET /api/categories/{id}/servicemen/`
- `POST /api/categories/`
- `PATCH /api/categories/{id}/`

### Service Requests
- `POST /api/service-requests/`
- `GET /api/service-requests/`
- `GET /api/service-requests/{id}/`
- `PATCH /api/service-requests/{id}/status/`

### Admin
- `GET /api/admin/pending-assignments/`
- `POST /api/admin/assign-serviceman/`
- `GET /api/admin/pricing-review/`
- `PATCH /api/admin/update-final-cost/`
- `GET /api/admin/analytics/revenue/`
- `GET /api/admin/analytics/servicemen/`
- `GET /api/admin/analytics/categories/`

### Serviceman
- `GET /api/serviceman/assigned-jobs/`
- `POST /api/serviceman/accept-job/{id}/`
- `POST /api/serviceman/decline-job/{id}/`
- `POST /api/serviceman/submit-estimate/`
- `POST /api/serviceman/complete-job/{id}/`
- `GET /api/serviceman/earnings/`

### Payments
- `POST /api/payments/initialize/`
- `POST /api/payments/webhook/`
- `GET /api/payments/verify/{reference}/`

### Negotiations
- `POST /api/negotiations/`
- `POST /api/negotiations/{id}/respond/`
- `GET /api/negotiations/?request_id=X`
- `POST /api/negotiations/{id}/check-with-serviceman/`

### Notifications
- `GET /api/notifications/`
- `PATCH /api/notifications/{id}/read/`
- `PATCH /api/notifications/mark-all-read/`
- `GET /api/notifications/unread-count/`

### Ratings
- `POST /api/ratings/`
- `GET /api/ratings/?serviceman_id=X`

---

## 16. SUCCESS CRITERIA

- Every booking/payment/negotiation/notification flow works end-to-end with backend
- All validation and security rules enforced
- Real-time notifications always delivered
- Dual-channel notifications visible (dashboard & email)
- All roles have full-featured dashboards
- 80%+ frontend test coverage
- UI is modern, responsive, professional

---

**Build the entire frontend as specified. Use the API contract and flow exactly as described. No shortcuts.**
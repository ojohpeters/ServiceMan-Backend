# Serviceman Platform Frontend — ULTRA-DETAILED IMPLEMENTATION PROMPT

You are an expert AI frontend developer. You must build a **production-grade, real-world frontend** for the Serviceman Platform, a three-sided service marketplace for Clients, Servicemen, and Admins.

Your output MUST:
- Use the exact backend API endpoints, models, and business logic as documented below.
- Deliver a complete, ready-to-run, responsive web application.
- Include all flows, validation, security, state management, and UX best practices.
- Implement all critical booking, payment, negotiation, notification, and admin dashboard features.
- Be modular, maintainable, and easy for a real dev team to extend.

---

## 1. TECH STACK & PROJECT SETUP

**MANDATORY:**
- Use [React](https://react.dev/) (v18+) with TypeScript.
- Use [Next.js](https://nextjs.org/) (v13+) or [Vite](https://vitejs.dev/) for optimal SSR/SSG and fast dev.
- Use [Redux Toolkit](https://redux-toolkit.js.org/) for global state.
- Use [React Query](https://tanstack.com/query/latest/) (or equivalent) for data fetching/caching.
- Use [Tailwind CSS](https://tailwindcss.com/) for rapid, responsive design.
- Use [Formik](https://formik.org/) + [Yup](https://github.com/jquense/yup) for forms/validation.
- Use [socket.io-client](https://socket.io/) or [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) for real-time notifications.
- Store JWT securely (httpOnly cookie preferred, or encrypted localStorage).
- Use environment variables for API base URL, Paystack public key, etc.

**Optional/Recommended:**
- Use [Ant Design](https://ant.design/) or [MUI](https://mui.com/) for pro UI components.
- PWA support (add manifest, offline fallback).
- Sentry (for error monitoring).
- Vercel/Netlify ready.

---

## 2. ROUTING & LAYOUT

- `/` — Landing page (marketing, CTA, features, testimonials)
- `/login`, `/register`, `/forgot-password`, `/reset-password` — Auth flows
- `/verify-email?token=...` — Email verification
- `/dashboard` — Role-based: routes to `/client`, `/serviceman`, or `/admin` dashboard
- `/categories` — Browse categories
- `/categories/[id]` — View category details + servicemen list
- `/servicemen/[id]` — Serviceman public profile
- `/service-requests/[id]` — Service request details (conditional on user role)
- `/notifications` — List of notifications, mark as read
- `/admin` — Admin dashboard
- `/admin/assignments`, `/admin/analytics`, etc.
- `/negotiations/[requestId]` — Negotiation chat

---

## 3. AUTHENTICATION & SECURITY

- Use JWT auth as issued by backend.
- Store JWT in httpOnly cookie if possible (for XSS safety) or encrypted localStorage (with auto logout on expiry).
- All API requests MUST attach JWT.
- On 401/403, auto-logout and redirect to `/login`.
- Require email verification before allowing bookings/payments.
- Password fields: min 8 chars, uppercase, lowercase, number (Yup validation).
- Block UI after 5 failed login attempts/minute (rate limit).

---

## 4. CLIENT FLOWS

### Onboarding
- Register → Email verification → Login

### Booking
- Browse categories (`GET /api/categories/`)
- View servicemen in category (`GET /api/categories/{id}/servicemen/`)
- View serviceman profile (rating, jobs, bio, experience)
- "Book Now" → Date picker modal
- Auto-detect emergency: if date is within 2 days, show emergency toggle ON (cannot disable if auto-flag)
- Manual toggle for emergency (if not auto-flagged)
- Dynamic display: Booking fee ₦5,000 (emergency) or ₦2,000 (normal)
- Submit booking → `POST /api/service-requests/` (show summary, confirm)
- Payment: Initialize Paystack via `POST /api/payments/initialize/`, redirect to Paystack checkout
- After payment, show success and status ("Pending Admin Assignment")

### Track Requests
- `/dashboard` shows active/past requests, status, actions (pay, negotiate, rate, etc.)
- View request details (`GET /api/service-requests/{id}/`)
- If negotiation allowed, show negotiation UI (chat-style, with message history)
- If payment required, show Paystack payment button

### Notifications
- Notification bell with unread count (`GET /api/notifications/unread-count/`)
- List of notifications (`GET /api/notifications/`), mark as read

### Ratings
- After job completion, prompt client to rate serviceman (1-5 stars, review)
- Submit via `POST /api/ratings/`

---

## 5. SERVICEMAN FLOWS

### Dashboard
- `/dashboard` shows assigned jobs, pending inspections, completed jobs, earnings

### Job Actions
- Accept/decline assignment (actions visible if status=ASSIGNED_TO_SERVICEMAN)
- If declined, backup serviceman is notified
- Submit cost estimate after inspection (`POST /api/serviceman/submit-estimate/`)
- Mark job as complete (`POST /api/serviceman/complete-job/{id}/`)
- View earnings (`GET /api/serviceman/earnings/`)

### Profile
- View/update own profile (bio, experience, availability, category)
- View ratings and reviews

### Notifications
- All assignment/backup/approval/payment notifications (dual channel)
- Real-time dashboard updates (websocket or poll every 30s)

---

## 6. ADMIN FLOWS

### Dashboard
- `/admin` home: summary stats, quick links
- `/admin/assignments` — List pending assignments, assign serviceman + backup, set emergency flag
- `/admin/pricing` — View estimates, add markup, set final cost
- `/admin/negotiations` — Respond to negotiation threads
- `/admin/analytics` — Revenue, category stats, top servicemen
- `/admin/users` — Manage users/servicemen/clients, activate/deactivate
- `/admin/categories` — Manage categories

### Actions
- All admin status transitions require confirmation modals
- All admin-side notifications (dual channel)
- All lists are paginated, sortable, filterable

---

## 7. NEGOTIATION UI

- Chat-style negotiation view for each request (`GET /api/negotiations/?request_id=...`)
- Show all negotiation history, status (pending, accepted, countered, rejected)
- Allow client/admin to propose new price, counter, accept/reject
- If admin wants serviceman input, show "Ask Serviceman" button (sends message/notification to serviceman dashboard)
- All messages time-stamped

---

## 8. PAYMENTS

- Use Paystack JS SDK with public key from env
- All payment flows: Initial booking fee and final payment
- After payment, redirect back with status
- Display payment history per request
- Show errors clearly (failed, pending, duplicate, etc.)

---

## 9. NOTIFICATIONS

- Notification system must show both dashboard and email notifications
- Use websocket for real-time dashboard updates (or poll as fallback)
- Mark as read, mark all as read
- Unread badge on bell icon
- Show notification details (type, title, message, related request/payment)

---

## 10. EMAIL FLOWS

- All triggers must match backend:
    - Welcome, email verification, booking confirmation, assignment, backup, cost estimate, final cost, negotiation, payment received, job completed, emergency
- Show "Resend Email" button if user didn't receive critical email

---

## 11. SECURITY & VALIDATION

- All forms use Formik+Yup with strict validation matching backend rules
- No frontend admin-only actions exposed to non-admins
- All critical actions (payment, assignment, markup, negotiation) require user confirmation
- Never store Paystack secret keys in frontend; use only public key from env
- Use HTTPS for all API calls
- CORS origin must match backend whitelist

---

## 12. RESPONSIVE DESIGN

- Must be fully responsive: mobile-first, tablet, desktop
- Use Tailwind’s grid, flex, and responsive classes
- Test all flows on mobile viewport

---

## 13. TESTING

- Use Jest + React Testing Library for unit/integration tests
- Test all critical flows: booking, payment, negotiation, notifications
- Achieve minimum 80% coverage

---

## 14. DEPLOYMENT

- Ready for Vercel, Netlify, or similar
- `.env.example` with all needed variables (API URL, Paystack public key, etc.)
- `README.md` with setup, build, deploy steps

---

## 15. SUCCESS CRITERIA

- All booking/payment/negotiation/notification flows work E2E with backend
- All security and validation rules enforced
- Real-time notifications always delivered
- Dual-channel notifications visible to user in dashboard and via email
- All roles (Client, Serviceman, Admin) have fully functional dashboards
- 80%+ test coverage
- Professional, clean, modern, responsive UI

---

**Build the entire frontend as specified. No shortcuts. Use the API contract and business logic exactly as described.**
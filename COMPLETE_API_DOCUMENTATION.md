# 📚 ServiceMan Platform - Complete API Documentation

**Version**: 2.0.0  
**Base URL**: `http://localhost:8000` (Dev) | `https://serviceman-backend.onrender.com` (Prod)  
**Last Updated**: October 2025  

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Users & Profiles](#users--profiles)
3. [Servicemen Management](#servicemen-management)
4. [Skills](#skills)
5. [Categories](#categories)
6. [Service Requests](#service-requests)
7. [Payments](#payments)
8. [Ratings](#ratings)
9. [Negotiations](#negotiations)
10. [Notifications](#notifications)
11. [Admin Operations](#admin-operations)
12. [Analytics](#analytics)

---

## 🔐 Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 1.1 Register User

**Endpoint**: `POST /api/users/register/`  
**Auth**: None  
**Purpose**: Register new client or serviceman

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "user_type": "CLIENT",  // or "SERVICEMAN"
  "skill_ids": [1, 2, 3]  // Optional, for servicemen only
}
```

**Response (201):**
```json
{
  "id": 15,
  "username": "john_doe",
  "email": "john@example.com",
  "user_type": "CLIENT",
  "is_email_verified": false
}
```

**Notes:**
- Cannot create ADMIN through this endpoint
- Servicemen start as unapproved (`is_approved: false`)
- Email verification sent automatically
- Skills can be added during serviceman registration

---

### 1.2 Login / Get Token

**Endpoint**: `POST /api/users/token/`  
**Auth**: None  
**Purpose**: Get JWT access and refresh tokens

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Usage:**
```javascript
// Store tokens
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);

// Use in requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
}
```

---

### 1.3 Refresh Token

**Endpoint**: `POST /api/users/token/refresh/`  
**Auth**: None  
**Purpose**: Get new access token using refresh token

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 1.4 Verify Email

**Endpoint**: `GET /api/users/verify-email/?uid={uid}&token={token}`  
**Auth**: None  
**Purpose**: Verify email address from link

**Response (200):**
```json
{
  "detail": "Email verified successfully."
}
```

---

### 1.5 Resend Verification Email

**Endpoint**: `POST /api/users/resend-verification-email/`  
**Auth**: None

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "detail": "Verification email sent."
}
```

---

### 1.6 Request Password Reset

**Endpoint**: `POST /api/users/password-reset/`  
**Auth**: None

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "detail": "If the email exists in our system, a password reset link has been sent."
}
```

---

### 1.7 Confirm Password Reset

**Endpoint**: `POST /api/users/password-reset-confirm/?uid={uid}&token={token}`  
**Auth**: None

**Request:**
```json
{
  "password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "detail": "Password has been reset successfully."
}
```

---

## 👥 Users & Profiles

### 2.1 Get Current User

**Endpoint**: `GET /api/users/me/`  
**Auth**: Required

**Response (200):**
```json
{
  "id": 5,
  "username": "john_doe",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": true
}
```

---

### 2.2 Get User by ID

**Endpoint**: `GET /api/users/{user_id}/`  
**Auth**: Required  
**Access**: Admin can view all, users can view themselves, anyone can view servicemen

**Response (200):**
```json
{
  "id": 5,
  "username": "john_serviceman",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": true
}
```

---

### 2.3 Get Client Profile

**Endpoint**: `GET /api/users/clients/{client_id}/`  
**Auth**: Required (Admin or self)

**Response (200):**
```json
{
  "user": {
    "id": 10,
    "username": "client_john",
    "email": "client@example.com",
    "user_type": "CLIENT"
  },
  "phone_number": "+2348012345678",
  "address": "123 Main St, Lagos, Nigeria",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-10-18T14:30:00Z"
}
```

---

### 2.4 Get/Update Own Client Profile

**Endpoint**: `GET/PATCH /api/users/client-profile/`  
**Auth**: Required (Client)

**GET Response (200):**
```json
{
  "user": 10,
  "phone_number": "+2348012345678",
  "address": "123 Main St",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-10-18T14:30:00Z"
}
```

**PATCH Request:**
```json
{
  "phone_number": "+2348087654321",
  "address": "456 New Street"
}
```

---

### 2.5 Get/Update Own Serviceman Profile

**Endpoint**: `GET/PATCH /api/users/serviceman-profile/`  
**Auth**: Required (Serviceman)

**GET Response (200):**
```json
{
  "user": 5,
  "category": {
    "id": 2,
    "name": "Electrical"
  },
  "skills": [
    {
      "id": 1,
      "name": "Electrical Wiring",
      "category": "TECHNICAL"
    }
  ],
  "rating": "4.80",
  "total_jobs_completed": 45,
  "bio": "Expert electrician with 10 years experience",
  "years_of_experience": 10,
  "phone_number": "+2348012345678",
  "is_available": true,
  "active_jobs_count": 0,
  "availability_status": {
    "status": "available",
    "label": "Available",
    "message": "This serviceman is available for new jobs",
    "can_book": true
  },
  "is_approved": true,
  "approved_by": 1,
  "approved_at": "2025-10-15T12:00:00Z",
  "rejection_reason": "",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-10-18T14:30:00Z"
}
```

**PATCH Request:**
```json
{
  "bio": "Updated bio",
  "years_of_experience": 11,
  "phone_number": "+2348087654321",
  "skill_ids": [1, 2, 5]  // Update skills
}
```

---

## 👷 Servicemen Management

### 3.1 List All Servicemen

**Endpoint**: `GET /api/users/servicemen/`  
**Auth**: Public  
**Purpose**: List all approved servicemen with filtering

**Query Parameters:**
- `category` - Filter by category ID
- `is_available` - true/false
- `min_rating` - Minimum rating (e.g., 4.0)
- `search` - Search by name/username
- `ordering` - Sort by: rating, total_jobs_completed, years_of_experience, created_at
- `show_all` - true (admin only, shows unapproved too)

**Examples:**
```bash
# All servicemen
GET /api/users/servicemen/

# Available only
GET /api/users/servicemen/?is_available=true

# By category with 4.5+ rating
GET /api/users/servicemen/?category=1&min_rating=4.5

# Search "john"
GET /api/users/servicemen/?search=john

# Top rated
GET /api/users/servicemen/?ordering=-rating
```

**Response (200):**
```json
{
  "statistics": {
    "total_servicemen": 25,
    "available": 18,
    "busy": 7
  },
  "results": [
    {
      "user": 5,
      "category": {...},
      "skills": [...],
      "rating": "4.80",
      "total_jobs_completed": 45,
      "bio": "Expert electrician",
      "is_available": true,
      "active_jobs_count": 0,
      "availability_status": {
        "status": "available",
        "label": "Available",
        "can_book": true
      },
      "is_approved": true
    }
  ]
}
```

---

### 3.2 Get Serviceman Profile

**Endpoint**: `GET /api/users/servicemen/{serviceman_id}/`  
**Auth**: Public

**Response (200):**
Same format as 2.5 (serviceman profile)

---

### 3.3 Get Servicemen in Category

**Endpoint**: `GET /api/categories/{category_id}/servicemen/`  
**Auth**: Public

**Response (200):**
```json
{
  "category_id": 1,
  "total_servicemen": 10,
  "available_servicemen": 7,
  "busy_servicemen": 3,
  "availability_message": {
    "type": "success",
    "message": "7 servicemen are available for immediate service."
  },
  "servicemen": [
    {
      "id": 1,
      "full_name": "John Electrician",
      "username": "john_elec",
      "rating": 4.8,
      "total_jobs_completed": 45,
      "bio": "...",
      "years_of_experience": 10,
      "is_available": true,
      "active_jobs_count": 0,
      "availability_status": {
        "status": "available",
        "label": "Available",
        "badge_color": "green"
      }
    },
    {
      "id": 2,
      "is_available": false,
      "active_jobs_count": 2,
      "booking_warning": {
        "message": "This serviceman is currently working on 2 active job(s)",
        "recommendation": "Consider choosing an available serviceman",
        "can_still_book": true,
        "estimated_delay": "Service may be delayed"
      }
    }
  ]
}
```

---

## 💼 Skills

### 4.1 List All Skills

**Endpoint**: `GET /api/users/skills/`  
**Auth**: Public

**Query Parameters:**
- `category` - Filter by skill category (TECHNICAL, MANUAL, CREATIVE, PROFESSIONAL, OTHER)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Electrical Wiring",
    "category": "TECHNICAL",
    "description": "Installation and repair of electrical systems",
    "is_active": true,
    "created_at": "2025-10-01T10:00:00Z",
    "updated_at": "2025-10-01T10:00:00Z"
  }
]
```

---

### 4.2 Get Skill Details

**Endpoint**: `GET /api/users/skills/{skill_id}/`  
**Auth**: Public

**Response (200):**
Same format as single skill above

---

### 4.3 Create Skill (Admin)

**Endpoint**: `POST /api/users/skills/create/`  
**Auth**: Admin only

**Request:**
```json
{
  "name": "Smart Home Installation",
  "category": "TECHNICAL",
  "description": "Installation of smart home devices"
}
```

**Response (201):**
```json
{
  "id": 15,
  "name": "Smart Home Installation",
  "category": "TECHNICAL",
  "description": "Installation of smart home devices",
  "is_active": true,
  "created_at": "2025-10-18T12:00:00Z",
  "updated_at": "2025-10-18T12:00:00Z"
}
```

---

### 4.4 Update Skill (Admin)

**Endpoint**: `PUT/PATCH /api/users/skills/{skill_id}/update/`  
**Auth**: Admin only

**Request:**
```json
{
  "description": "Updated description"
}
```

---

### 4.5 Delete Skill (Admin - Soft Delete)

**Endpoint**: `DELETE /api/users/skills/{skill_id}/delete/`  
**Auth**: Admin only

**Response (204):** No content (skill marked as inactive)

---

### 4.6 Get Serviceman Skills

**Endpoint**: `GET /api/users/servicemen/{serviceman_id}/skills/`  
**Auth**: Public

**Response (200):**
```json
{
  "serviceman": {
    "id": 5,
    "username": "john_electrician",
    "full_name": "John Smith"
  },
  "skills": [
    {
      "id": 1,
      "name": "Electrical Wiring",
      "category": "TECHNICAL",
      "description": "..."
    }
  ]
}
```

---

### 4.7 Add Skills to Serviceman

**Endpoint**: `POST /api/users/servicemen/{serviceman_id}/skills/`  
**Auth**: Required (Serviceman themselves or Admin)

**Request:**
```json
{
  "skill_ids": [1, 5, 8]
}
```

**Response (200):**
```json
{
  "message": "Added 3 skill(s) successfully.",
  "skills": [...]
}
```

---

### 4.8 Remove Skills from Serviceman

**Endpoint**: `DELETE /api/users/servicemen/{serviceman_id}/skills/`  
**Auth**: Required (Serviceman themselves or Admin)

**Request:**
```json
{
  "skill_ids": [5]
}
```

**Response (200):**
```json
{
  "message": "Removed 1 skill(s) successfully.",
  "skills": [...]
}
```

---

## 📂 Categories

### 5.1 List Categories

**Endpoint**: `GET /api/categories/`  
**Auth**: Public

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Plumbing",
    "description": "Plumbing services including repairs and installations",
    "icon_url": "https://example.com/icons/plumbing.png",
    "is_active": true,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
]
```

---

### 5.2 Create Category (Admin)

**Endpoint**: `POST /api/categories/`  
**Auth**: Admin only

**Request:**
```json
{
  "name": "Electrical",
  "description": "Electrical services including wiring, repairs, and installations",
  "icon_url": "https://example.com/icons/electrical.png"
}
```

**Response (201):**
```json
{
  "id": 2,
  "name": "Electrical",
  "description": "...",
  "icon_url": "...",
  "is_active": true,
  "created_at": "2025-10-18T15:00:00Z",
  "updated_at": "2025-10-18T15:00:00Z"
}
```

---

### 5.3 Get/Update Category

**Endpoint**: `GET/PATCH /api/categories/{category_id}/`  
**Auth**: Public (GET), Admin (PATCH)

**PATCH Request:**
```json
{
  "description": "Updated description"
}
```

---

## 📝 Service Requests

### 6.1 List Service Requests

**Endpoint**: `GET /api/service-requests/`  
**Auth**: Required

**Access Control:**
- Admin: Sees all requests
- Client: Sees their own requests
- Serviceman: Sees assigned requests (primary or backup)

**Response (200):**
```json
[
  {
    "id": 123,
    "client": {
      "id": 10,
      "username": "client_john",
      "email": "client@example.com",
      "user_type": "CLIENT"
    },
    "serviceman": {
      "id": 5,
      "username": "john_serviceman"
    },
    "backup_serviceman": null,
    "category": {
      "id": 1,
      "name": "Plumbing"
    },
    "booking_date": "2025-10-25",
    "is_emergency": false,
    "auto_flagged_emergency": false,
    "status": "IN_PROGRESS",
    "initial_booking_fee": "2000.00",
    "serviceman_estimated_cost": "50000.00",
    "admin_markup_percentage": "10.00",
    "final_cost": "55000.00",
    "client_address": "123 Main St, Lagos",
    "service_description": "Fix leaking pipe in kitchen",
    "created_at": "2025-10-15T10:00:00Z",
    "updated_at": "2025-10-18T14:30:00Z",
    "inspection_completed_at": "2025-10-17T12:00:00Z",
    "work_completed_at": null
  }
]
```

---

### 6.2 Create Service Request (Client)

**Endpoint**: `POST /api/service-requests/`  
**Auth**: Required (Client only)

**Request:**
```json
{
  "category_id": 1,
  "booking_date": "2025-10-25",
  "is_emergency": false,
  "client_address": "123 Main St, Lagos",
  "service_description": "Fix leaking pipe in kitchen"
}
```

**Response (201):**
```json
{
  "id": 124,
  "status": "PENDING_ADMIN_ASSIGNMENT",
  "initial_booking_fee": "2000.00",  // Auto-calculated
  "is_emergency": false,
  "auto_flagged_emergency": false,  // Auto-flagged if date within 2 days
  ...
}
```

**Notes:**
- `is_emergency` auto-set to true if booking_date ≤ today + 2 days
- `initial_booking_fee` auto-calculated: ₦5,000 (emergency) or ₦2,000 (normal)
- Status starts as "PENDING_ADMIN_ASSIGNMENT"

---

### 6.3 Get Service Request Details

**Endpoint**: `GET /api/service-requests/{request_id}/`  
**Auth**: Required

**Access Control:**
- Admin: Can view all
- Client: Can view their own
- Serviceman: Can view if assigned (primary or backup)

**Response (200):**
Same format as 6.1

---

## 💳 Payments

### 7.1 Initialize Payment

**Endpoint**: `POST /api/payments/initialize/`  
**Auth**: Required

**Request:**
```json
{
  "service_request": 123,
  "payment_type": "INITIAL_BOOKING_FEE",  // or "FINAL_PAYMENT"
  "amount": 2000
}
```

**Response (201):**
```json
{
  "payment": {
    "id": 45,
    "service_request": 123,
    "payment_type": "INITIAL_BOOKING_FEE",
    "amount": "2000.00",
    "status": "PENDING",
    "paystack_reference": "123-INITIAL_BOOKING_FEE-1729267890.123",
    "created_at": "2025-10-18T15:00:00Z"
  },
  "paystack_url": "https://checkout.paystack.com/abc123..."
}
```

**Usage:**
```javascript
// Redirect user to paystack_url
window.location.href = data.paystack_url;
```

---

### 7.2 Paystack Webhook

**Endpoint**: `POST /api/payments/webhook/`  
**Auth**: None (Paystack signature verified)

**Purpose**: Receives payment confirmation from Paystack

**Note**: This is called by Paystack, not your frontend

---

### 7.3 Verify Payment

**Endpoint**: `POST /api/payments/verify/`  
**Auth**: Public

**Request:**
```json
{
  "reference": "123-INITIAL_BOOKING_FEE-1729267890.123"
}
```

**Response (200):**
```json
{
  "status": "SUCCESSFUL"  // or "FAILED", "PENDING"
}
```

---

## ⭐ Ratings

### 8.1 Create Rating

**Endpoint**: `POST /api/ratings/create/`  
**Auth**: Required (Client who owns the service request)

**Request:**
```json
{
  "service_request": 123,
  "rating": 5,
  "review": "Excellent service! Very professional and timely."
}
```

**Response (201):**
```json
{
  "id": 78,
  "service_request": 123,
  "client": 10,
  "serviceman": 5,
  "rating": 5,
  "review": "Excellent service!...",
  "created_at": "2025-10-18T16:00:00Z"
}
```

**Notes:**
- Automatically updates serviceman's average rating
- Increments total_jobs_completed
- Can only rate once per service request

---

### 8.2 List Ratings

**Endpoint**: `GET /api/ratings/`  
**Auth**: Public

**Query Parameters:**
- `serviceman_id` - Filter by serviceman

**Example:**
```bash
GET /api/ratings/?serviceman_id=5
```

**Response (200):**
```json
[
  {
    "id": 78,
    "service_request": 123,
    "client": {
      "id": 10,
      "username": "client_john"
    },
    "serviceman": {
      "id": 5,
      "username": "john_serviceman"
    },
    "rating": 5,
    "review": "Excellent service!",
    "created_at": "2025-10-18T16:00:00Z"
  }
]
```

---

## 💬 Negotiations

### 9.1 List Negotiations

**Endpoint**: `GET /api/negotiations/`  
**Auth**: Required

**Query Parameters:**
- `request_id` - Filter by service request (required)

**Example:**
```bash
GET /api/negotiations/?request_id=123
```

**Response (200):**
```json
[
  {
    "id": 1,
    "service_request": 123,
    "proposed_by": {
      "id": 10,
      "username": "client_john"
    },
    "proposed_amount": "45000.00",
    "message": "Can you reduce the price to ₦45,000?",
    "status": "PENDING",
    "created_at": "2025-10-17T14:00:00Z"
  },
  {
    "id": 2,
    "proposed_by": {
      "id": 1,
      "username": "admin"
    },
    "proposed_amount": "50000.00",
    "message": "We can offer ₦50,000 as final price",
    "status": "COUNTERED",
    "created_at": "2025-10-17T15:00:00Z"
  }
]
```

---

### 9.2 Create Negotiation

**Endpoint**: `POST /api/negotiations/create/`  
**Auth**: Required

**Request:**
```json
{
  "service_request": 123,
  "proposed_amount": 45000,
  "message": "Can you reduce the price to ₦45,000?"
}
```

**Response (201):**
```json
{
  "id": 3,
  "service_request": 123,
  "proposed_by": 10,
  "proposed_amount": "45000.00",
  "message": "Can you reduce the price to ₦45,000?",
  "status": "PENDING",
  "created_at": "2025-10-18T16:30:00Z"
}
```

---

### 9.3 Accept Negotiation

**Endpoint**: `POST /api/negotiations/{negotiation_id}/accept/`  
**Auth**: Required

**Response (200):**
```json
{
  "status": "ACCEPTED"
}
```

---

### 9.4 Counter Negotiation

**Endpoint**: `POST /api/negotiations/{negotiation_id}/counter/`  
**Auth**: Required

**Request:**
```json
{
  "proposed_amount": 48000,
  "message": "We can meet at ₦48,000"
}
```

**Response (200):**
```json
{
  "id": 4,
  "service_request": 123,
  "proposed_amount": "48000.00",
  "message": "We can meet at ₦48,000",
  "status": "COUNTERED",
  "created_at": "2025-10-18T17:00:00Z"
}
```

---

## 🔔 Notifications

### 10.1 List User's Notifications

**Endpoint**: `GET /api/notifications/`  
**Auth**: Required

**Response (200):**
```json
[
  {
    "id": 45,
    "user": 5,
    "notification_type": "SERVICE_ASSIGNED",
    "title": "New Service Request Assigned",
    "message": "You have been assigned to service request #123",
    "service_request": 123,
    "is_read": false,
    "sent_to_email": true,
    "email_sent_at": "2025-10-18T14:30:00Z",
    "created_at": "2025-10-18T14:30:00Z"
  }
]
```

---

### 10.2 Get Unread Count

**Endpoint**: `GET /api/notifications/unread-count/`  
**Auth**: Required

**Response (200):**
```json
{
  "unread_count": 3
}
```

---

### 10.3 Mark Notification as Read

**Endpoint**: `PATCH /api/notifications/{notification_id}/read/`  
**Auth**: Required

**Response (200):**
```json
{
  "detail": "Notification marked as read."
}
```

---

### 10.4 Mark All as Read

**Endpoint**: `PATCH /api/notifications/mark-all-read/`  
**Auth**: Required

**Response (200):**
```json
{
  "detail": "All notifications marked as read."
}
```

---

### 10.5 Send Notification (Admin)

**Endpoint**: `POST /api/notifications/send/`  
**Auth**: Admin only

**Request:**
```json
{
  "user_id": 5,
  "title": "Service Request Assigned",
  "message": "You have been assigned to service request #123",
  "notification_type": "SERVICE_ASSIGNED",
  "service_request_id": 123
}
```

**Required**: `user_id`, `title`, `message`  
**Optional**: `notification_type`, `service_request_id`

**Response (201):**
```json
{
  "detail": "Notification sent successfully",
  "notification": {
    "id": 46,
    "user": 5,
    "title": "Service Request Assigned",
    "message": "...",
    "is_read": false,
    "created_at": "2025-10-18T17:30:00Z"
  },
  "email_queued": true,
  "recipient": {
    "id": 5,
    "username": "john_serviceman",
    "email": "john@example.com",
    "user_type": "SERVICEMAN"
  }
}
```

---

## 👑 Admin Operations

### 11.1 Create Admin User

**Endpoint**: `POST /api/users/admin/create/`  
**Auth**: Admin only

**Request:**
```json
{
  "username": "new_admin",
  "email": "admin@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Admin"
}
```

**Response (201):**
```json
{
  "id": 20,
  "username": "new_admin",
  "email": "admin@example.com",
  "user_type": "ADMIN",
  "is_email_verified": true
}
```

---

### 11.2 List Pending Serviceman Applications

**Endpoint**: `GET /api/users/admin/pending-servicemen/`  
**Auth**: Admin only

**Response (200):**
```json
{
  "total_pending": 5,
  "pending_applications": [
    {
      "user": 15,
      "category": null,
      "skills": [],
      "bio": "Experienced electrician",
      "years_of_experience": 10,
      "phone_number": "+2348012345678",
      "is_approved": false,
      "rejection_reason": "",
      "created_at": "2025-10-18T10:00:00Z"
    }
  ]
}
```

---

### 11.3 Approve Serviceman

**Endpoint**: `POST /api/users/admin/approve-serviceman/`  
**Auth**: Admin only

**Request:**
```json
{
  "serviceman_id": 15,
  "category_id": 2,
  "notes": "Approved for electrical work"
}
```

**Required**: `serviceman_id`  
**Optional**: `category_id`, `notes`

**Response (200):**
```json
{
  "detail": "Serviceman application approved successfully",
  "serviceman": {
    "id": 15,
    "username": "john_electrician",
    "full_name": "John Smith",
    "email": "john@example.com"
  },
  "approved_by": "admin",
  "approved_at": "2025-10-18T17:45:00Z",
  "category": {
    "id": 2,
    "name": "Electrical"
  }
}
```

---

### 11.4 Reject Serviceman

**Endpoint**: `POST /api/users/admin/reject-serviceman/`  
**Auth**: Admin only

**Request:**
```json
{
  "serviceman_id": 15,
  "rejection_reason": "Insufficient documentation provided"
}
```

**Response (200):**
```json
{
  "detail": "Serviceman application rejected",
  "serviceman": {
    "id": 15,
    "username": "john_electrician",
    "email": "john@example.com"
  },
  "rejected_by": "admin",
  "rejection_reason": "Insufficient documentation provided"
}
```

---

### 11.5 Assign Serviceman to Category

**Endpoint**: `POST /api/users/admin/assign-category/`  
**Auth**: Admin only

**Request:**
```json
{
  "serviceman_id": 5,
  "category_id": 2
}
```

**Response (200):**
```json
{
  "detail": "Category assignment updated successfully",
  "serviceman": {
    "id": 5,
    "username": "john_serviceman",
    "full_name": "John Smith"
  },
  "previous_category": {
    "id": 1,
    "name": "Plumbing"
  },
  "new_category": {
    "id": 2,
    "name": "Electrical"
  }
}
```

---

### 11.6 Bulk Assign Category

**Endpoint**: `POST /api/users/admin/bulk-assign-category/`  
**Auth**: Admin only

**Request:**
```json
{
  "serviceman_ids": [5, 6, 7, 8, 9],
  "category_id": 2
}
```

**Response (200):**
```json
{
  "detail": "Successfully assigned 5 servicemen to category 'Electrical'",
  "category": {
    "id": 2,
    "name": "Electrical"
  },
  "updated_servicemen": [
    {
      "id": 5,
      "username": "john_elec",
      "full_name": "John Smith"
    }
  ],
  "total_updated": 5,
  "not_found": 0
}
```

---

### 11.7 Get Servicemen by Category

**Endpoint**: `GET /api/users/admin/servicemen-by-category/`  
**Auth**: Admin only

**Response (200):**
```json
{
  "total_servicemen": 25,
  "total_categories": 5,
  "categories": [
    {
      "category": {
        "id": 1,
        "name": "Plumbing",
        "description": "..."
      },
      "servicemen_count": 8,
      "servicemen": [
        {
          "id": 1,
          "username": "plumber1",
          "full_name": "John Plumber",
          "email": "john@example.com",
          "is_available": true,
          "is_approved": true,
          "rating": 4.8,
          "total_jobs_completed": 45
        }
      ]
    },
    {
      "category": null,
      "servicemen_count": 3,
      "servicemen": [...],
      "note": "Unassigned servicemen - no category set"
    }
  ]
}
```

---

## 📊 Analytics

### 12.1 Revenue Analytics (Admin)

**Endpoint**: `GET /api/ratings/analytics/revenue/`  
**Auth**: Admin only

**Response (200):**
```json
{
  "total_revenue": 500000,
  "this_month": 125000
}
```

---

### 12.2 Top Servicemen Analytics (Admin)

**Endpoint**: `GET /api/ratings/analytics/servicemen/`  
**Auth**: Admin only

**Response (200):**
```json
[
  {
    "id": 5,
    "full_name": "John Electrician",
    "rating": "4.90",
    "total_jobs_completed": 120
  },
  {
    "id": 8,
    "full_name": "Mike Plumber",
    "rating": "4.85",
    "total_jobs_completed": 98
  }
]
```

---

### 12.3 Top Categories Analytics (Admin)

**Endpoint**: `GET /api/ratings/analytics/categories/`  
**Auth**: Admin only

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Plumbing",
    "request_count": 234
  },
  {
    "id": 2,
    "name": "Electrical",
    "request_count": 198
  }
]
```

---

## 📊 Complete Endpoint Reference Table

### Authentication & Users (15 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/users/register/` | None | Register user |
| POST | `/api/users/token/` | None | Login |
| POST | `/api/users/token/refresh/` | None | Refresh token |
| GET | `/api/users/verify-email/` | None | Verify email |
| POST | `/api/users/resend-verification-email/` | None | Resend verification |
| POST | `/api/users/password-reset/` | None | Request reset |
| POST | `/api/users/password-reset-confirm/` | None | Confirm reset |
| GET | `/api/users/me/` | Yes | Current user |
| GET | `/api/users/{id}/` | Yes | User by ID |
| GET | `/api/users/clients/{id}/` | Admin/Self | Client profile |
| GET/PATCH | `/api/users/client-profile/` | Client | Own client profile |
| GET/PATCH | `/api/users/serviceman-profile/` | Serviceman | Own serviceman profile |
| GET | `/api/users/servicemen/` | Public | List all servicemen |
| GET | `/api/users/servicemen/{id}/` | Public | Serviceman profile |

### Skills (6 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/users/skills/` | Public | List skills |
| GET | `/api/users/skills/{id}/` | Public | Skill details |
| POST | `/api/users/skills/create/` | Admin | Create skill |
| PUT/PATCH | `/api/users/skills/{id}/update/` | Admin | Update skill |
| DELETE | `/api/users/skills/{id}/delete/` | Admin | Delete skill |
| GET/POST/DELETE | `/api/users/servicemen/{id}/skills/` | Mixed | Manage skills |

### Admin Operations (7 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/users/admin/create/` | Admin | Create admin |
| GET | `/api/users/admin/pending-servicemen/` | Admin | Pending applications |
| POST | `/api/users/admin/approve-serviceman/` | Admin | Approve serviceman |
| POST | `/api/users/admin/reject-serviceman/` | Admin | Reject serviceman |
| POST | `/api/users/admin/assign-category/` | Admin | Assign category |
| POST | `/api/users/admin/bulk-assign-category/` | Admin | Bulk assign |
| GET | `/api/users/admin/servicemen-by-category/` | Admin | View by category |

### Categories (3 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/categories/` | Public | List categories |
| POST | `/api/categories/` | Admin | Create category |
| GET/PATCH | `/api/categories/{id}/` | Public/Admin | Get/Update category |
| GET | `/api/categories/{id}/servicemen/` | Public | Servicemen in category |

### Service Requests (3 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/service-requests/` | Yes | List requests |
| POST | `/api/service-requests/` | Client | Create request |
| GET | `/api/service-requests/{id}/` | Yes | Request details |

### Payments (3 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/payments/initialize/` | Yes | Initialize payment |
| POST | `/api/payments/webhook/` | None | Paystack webhook |
| POST | `/api/payments/verify/` | Public | Verify payment |

### Ratings (2 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/ratings/create/` | Client | Create rating |
| GET | `/api/ratings/` | Public | List ratings |

### Negotiations (4 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/negotiations/` | Yes | List negotiations |
| POST | `/api/negotiations/create/` | Yes | Create negotiation |
| POST | `/api/negotiations/{id}/accept/` | Yes | Accept negotiation |
| POST | `/api/negotiations/{id}/counter/` | Yes | Counter offer |

### Notifications (5 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/notifications/` | Yes | List notifications |
| POST | `/api/notifications/send/` | Admin | Send notification |
| GET | `/api/notifications/unread-count/` | Yes | Unread count |
| PATCH | `/api/notifications/{id}/read/` | Yes | Mark as read |
| PATCH | `/api/notifications/mark-all-read/` | Yes | Mark all read |

### Analytics (3 endpoints)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/ratings/analytics/revenue/` | Admin | Revenue stats |
| GET | `/api/ratings/analytics/servicemen/` | Admin | Top servicemen |
| GET | `/api/ratings/analytics/categories/` | Admin | Top categories |

**Total Endpoints**: 50+

---

## 🔑 Authentication Patterns

### Pattern 1: No Auth Required
```javascript
// Public endpoints
const response = await fetch('/api/categories/');
const data = await response.json();
```

### Pattern 2: User Auth Required
```javascript
// Authenticated endpoints
const token = localStorage.getItem('access_token');

const response = await fetch('/api/users/me/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
```

### Pattern 3: Admin Only
```javascript
// Admin endpoints
const token = localStorage.getItem('access_token');

const response = await fetch('/api/users/admin/pending-servicemen/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Returns 403 if not admin
if (response.status === 403) {
  alert('Admin access required');
}
```

### Pattern 4: Role-Based Access
```javascript
// Different responses based on user role
const response = await fetch('/api/service-requests/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Admin sees all, client sees theirs, serviceman sees assigned
```

---

## 📦 Complete Frontend Integration Example

```javascript
// src/services/api.js - Complete API Client

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Helper function
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(API_BASE_URL + endpoint, {
    ...options,
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  // Handle token expiration
  if (response.status === 401) {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      // Try to refresh
      const refreshResponse = await fetch(API_BASE_URL + '/api/users/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
      });
      
      if (refreshResponse.ok) {
        const { access } = await refreshResponse.json();
        localStorage.setItem('access_token', access);
        
        // Retry original request
        return fetch(API_BASE_URL + endpoint, {
          ...options,
          headers: {
            'Authorization': `Bearer ${access}`,
            'Content-Type': 'application/json',
            ...options.headers
          }
        });
      }
    }
    
    // Redirect to login
    localStorage.clear();
    window.location.href = '/login';
  }
  
  return response;
}

// Export all API functions
export const API = {
  // Auth
  register: (data) => 
    apiRequest('/api/users/register/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  login: (username, password) =>
    apiRequest('/api/users/token/', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    }),
  
  refreshToken: (refresh) =>
    apiRequest('/api/users/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh })
    }),
  
  getCurrentUser: () => 
    apiRequest('/api/users/me/'),
  
  // Users
  getUserById: (userId) => 
    apiRequest(`/api/users/${userId}/`),
  
  getClientProfile: (clientId) => 
    apiRequest(`/api/users/clients/${clientId}/`),
  
  updateClientProfile: (data) =>
    apiRequest('/api/users/client-profile/', {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),
  
  updateServicemanProfile: (data) =>
    apiRequest('/api/users/serviceman-profile/', {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),
  
  // Servicemen
  getAllServicemen: (filters = {}) => {
    const params = new URLSearchParams(filters);
    return apiRequest(`/api/users/servicemen/?${params}`);
  },
  
  getServicemanProfile: (servicemanId) =>
    apiRequest(`/api/users/servicemen/${servicemanId}/`),
  
  // Skills
  getSkills: (category = null) => {
    const url = category 
      ? `/api/users/skills/?category=${category}` 
      : '/api/users/skills/';
    return apiRequest(url);
  },
  
  createSkill: (data) =>
    apiRequest('/api/users/skills/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  getServicemanSkills: (servicemanId) =>
    apiRequest(`/api/users/servicemen/${servicemanId}/skills/`),
  
  addSkillsToServiceman: (servicemanId, skillIds) =>
    apiRequest(`/api/users/servicemen/${servicemanId}/skills/`, {
      method: 'POST',
      body: JSON.stringify({ skill_ids: skillIds })
    }),
  
  // Categories
  getCategories: () => 
    apiRequest('/api/categories/'),
  
  createCategory: (data) =>
    apiRequest('/api/categories/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  getCategoryServicemen: (categoryId) =>
    apiRequest(`/api/categories/${categoryId}/servicemen/`),
  
  // Service Requests
  getServiceRequests: () =>
    apiRequest('/api/service-requests/'),
  
  createServiceRequest: (data) =>
    apiRequest('/api/service-requests/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  getServiceRequest: (requestId) =>
    apiRequest(`/api/service-requests/${requestId}/`),
  
  // Payments
  initializePayment: (data) =>
    apiRequest('/api/payments/initialize/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  verifyPayment: (reference) =>
    apiRequest('/api/payments/verify/', {
      method: 'POST',
      body: JSON.stringify({ reference })
    }),
  
  // Ratings
  createRating: (data) =>
    apiRequest('/api/ratings/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  getRatings: (servicemanId = null) => {
    const url = servicemanId 
      ? `/api/ratings/?serviceman_id=${servicemanId}` 
      : '/api/ratings/';
    return apiRequest(url);
  },
  
  // Negotiations
  getNegotiations: (requestId) =>
    apiRequest(`/api/negotiations/?request_id=${requestId}`),
  
  createNegotiation: (data) =>
    apiRequest('/api/negotiations/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  acceptNegotiation: (negotiationId) =>
    apiRequest(`/api/negotiations/${negotiationId}/accept/`, {
      method: 'POST'
    }),
  
  counterNegotiation: (negotiationId, amount, message) =>
    apiRequest(`/api/negotiations/${negotiationId}/counter/`, {
      method: 'POST',
      body: JSON.stringify({ 
        proposed_amount: amount, 
        message 
      })
    }),
  
  // Notifications
  getNotifications: () =>
    apiRequest('/api/notifications/'),
  
  getUnreadCount: () =>
    apiRequest('/api/notifications/unread-count/'),
  
  markAsRead: (notificationId) =>
    apiRequest(`/api/notifications/${notificationId}/read/`, {
      method: 'PATCH'
    }),
  
  markAllRead: () =>
    apiRequest('/api/notifications/mark-all-read/', {
      method: 'PATCH'
    }),
  
  sendNotification: (data) =>
    apiRequest('/api/notifications/send/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  // Admin - Approvals
  getPendingServicemen: () =>
    apiRequest('/api/users/admin/pending-servicemen/'),
  
  approveServiceman: (servicemanId, categoryId, notes) =>
    apiRequest('/api/users/admin/approve-serviceman/', {
      method: 'POST',
      body: JSON.stringify({ 
        serviceman_id: servicemanId, 
        category_id: categoryId,
        notes
      })
    }),
  
  rejectServiceman: (servicemanId, reason) =>
    apiRequest('/api/users/admin/reject-serviceman/', {
      method: 'POST',
      body: JSON.stringify({ 
        serviceman_id: servicemanId, 
        rejection_reason: reason 
      })
    }),
  
  // Admin - Categories
  assignCategory: (servicemanId, categoryId) =>
    apiRequest('/api/users/admin/assign-category/', {
      method: 'POST',
      body: JSON.stringify({ 
        serviceman_id: servicemanId, 
        category_id: categoryId 
      })
    }),
  
  bulkAssignCategory: (servicemanIds, categoryId) =>
    apiRequest('/api/users/admin/bulk-assign-category/', {
      method: 'POST',
      body: JSON.stringify({ 
        serviceman_ids: servicemanIds, 
        category_id: categoryId 
      })
    }),
  
  getServicemenByCategory: () =>
    apiRequest('/api/users/admin/servicemen-by-category/'),
  
  createAdmin: (data) =>
    apiRequest('/api/users/admin/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  
  // Analytics
  getRevenueAnalytics: () =>
    apiRequest('/api/ratings/analytics/revenue/'),
  
  getTopServicemen: () =>
    apiRequest('/api/ratings/analytics/servicemen/'),
  
  getTopCategories: () =>
    apiRequest('/api/ratings/analytics/categories/')
};

export default API;
```

---

## 🎯 Common Workflows

### Workflow 1: Client Books Service

```javascript
async function clientBookingFlow() {
  // 1. Browse categories
  const categories = await API.getCategories();
  
  // 2. View servicemen in category
  const categoryServicemen = await API.getCategoryServicemen(categoryId);
  
  // 3. Check availability
  const serviceman = categoryServicemen.servicemen[0];
  if (!serviceman.is_available) {
    // Show warning
    alert(serviceman.availability_status.warning);
  }
  
  // 4. Create service request
  const request = await API.createServiceRequest({
    category_id: categoryId,
    booking_date: "2025-10-25",
    client_address: "123 Main St",
    service_description: "Fix leaking pipe"
  });
  
  // 5. Initialize payment
  const payment = await API.initializePayment({
    service_request: request.id,
    payment_type: "INITIAL_BOOKING_FEE",
    amount: request.initial_booking_fee
  });
  
  // 6. Redirect to Paystack
  window.location.href = payment.paystack_url;
}
```

### Workflow 2: Admin Assigns Serviceman

```javascript
async function adminAssignmentFlow(requestId) {
  // 1. Get service request
  const request = await API.getServiceRequest(requestId);
  
  // 2. Get available servicemen in category
  const servicemen = await API.getAllServicemen({
    category: request.category.id,
    is_available: true,
    ordering: '-rating'
  });
  
  // 3. Select serviceman (or let admin choose)
  const servicemanId = servicemen.results[0].user;
  
  // 4. Assign to request (via Django admin or custom endpoint)
  // This would need an admin endpoint to update service request
  
  // 5. Notify serviceman
  await API.sendNotification({
    user_id: servicemanId,
    title: 'New Service Assignment',
    message: `You have been assigned to service request #${requestId}`,
    notification_type: 'SERVICE_ASSIGNED',
    service_request_id: requestId
  });
}
```

### Workflow 3: Admin Approves Serviceman

```javascript
async function adminApprovalFlow() {
  // 1. Get pending applications
  const pending = await API.getPendingServicemen();
  
  console.log(`${pending.total_pending} applications pending`);
  
  // 2. Review application
  const application = pending.pending_applications[0];
  
  // 3. Approve with category
  const result = await API.approveServiceman(
    application.user,
    2,  // category_id
    'Verified credentials'
  );
  
  alert(result.detail);  // "Serviceman application approved successfully"
}
```

### Workflow 4: Serviceman Checks Status

```javascript
async function servicemanDashboardFlow() {
  // 1. Get current user
  const user = await API.getCurrentUser();
  
  // 2. Get profile
  const profile = await API.getServicemanProfile(user.id);
  
  // 3. Check approval status
  if (!profile.is_approved) {
    return <PendingApprovalScreen />;
  }
  
  // 4. Get assigned jobs
  const requests = await API.getServiceRequests();
  
  // 5. Get notifications
  const notifications = await API.getNotifications();
  const unreadCount = await API.getUnreadCount();
  
  return {
    profile,
    requests,
    notifications,
    unreadCount
  };
}
```

---

## 🚨 Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process data |
| 201 | Created | Resource created successfully |
| 204 | No Content | Deletion successful |
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Refresh token or redirect to login |
| 403 | Forbidden | Show "No permission" message |
| 404 | Not Found | Show "Not found" message |
| 500 | Server Error | Show "Server error, try again" |

### Error Handling Example
```javascript
async function handleApiCall(apiFunction) {
  try {
    const response = await apiFunction();
    
    if (!response.ok) {
      const error = await response.json();
      
      switch (response.status) {
        case 400:
          return { success: false, errors: error };
        case 401:
          localStorage.clear();
          window.location.href = '/login';
          break;
        case 403:
          alert('Permission denied');
          break;
        case 404:
          alert('Resource not found');
          break;
        case 500:
          alert('Server error. Please try again.');
          break;
        default:
          alert('An error occurred');
      }
      
      return { success: false, error: error.detail };
    }
    
    const data = await response.json();
    return { success: true, data };
    
  } catch (error) {
    console.error('API Error:', error);
    return { success: false, error: error.message };
  }
}

// Usage
const result = await handleApiCall(() => API.getServiceRequests());
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}
```

---

## 📱 TypeScript Type Definitions

```typescript
// types/api.ts

export interface User {
  id: number;
  username: string;
  email: string;
  user_type: 'ADMIN' | 'SERVICEMAN' | 'CLIENT';
  is_email_verified: boolean;
}

export interface Skill {
  id: number;
  name: string;
  category: 'TECHNICAL' | 'MANUAL' | 'CREATIVE' | 'PROFESSIONAL' | 'OTHER';
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AvailabilityStatus {
  status: 'available' | 'busy';
  label: string;
  message: string;
  can_book: boolean;
  active_jobs?: number;
  warning?: string;
  badge_color?: string;
}

export interface ServicemanProfile {
  user: number;
  category: Category | null;
  skills: Skill[];
  rating: string;
  total_jobs_completed: number;
  bio: string;
  years_of_experience: number | null;
  phone_number: string;
  is_available: boolean;
  active_jobs_count: number;
  availability_status: AvailabilityStatus;
  is_approved: boolean;
  approved_by: number | null;
  approved_at: string | null;
  rejection_reason: string;
  created_at: string;
  updated_at: string;
}

export interface ClientProfile {
  user: User;
  phone_number: string;
  address: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  icon_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceRequest {
  id: number;
  client: User;
  serviceman: User | null;
  backup_serviceman: User | null;
  category: Category;
  booking_date: string;
  is_emergency: boolean;
  auto_flagged_emergency: boolean;
  status: ServiceRequestStatus;
  initial_booking_fee: string;
  serviceman_estimated_cost: string | null;
  admin_markup_percentage: string;
  final_cost: string | null;
  client_address: string;
  service_description: string;
  created_at: string;
  updated_at: string;
  inspection_completed_at: string | null;
  work_completed_at: string | null;
}

export type ServiceRequestStatus = 
  | 'PENDING_ADMIN_ASSIGNMENT'
  | 'ASSIGNED_TO_SERVICEMAN'
  | 'SERVICEMAN_INSPECTED'
  | 'AWAITING_CLIENT_APPROVAL'
  | 'NEGOTIATING'
  | 'AWAITING_PAYMENT'
  | 'PAYMENT_CONFIRMED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED';

export interface Payment {
  id: number;
  service_request: number;
  payment_type: 'INITIAL_BOOKING_FEE' | 'FINAL_PAYMENT';
  amount: string;
  status: 'PENDING' | 'SUCCESSFUL' | 'FAILED';
  paystack_reference: string;
  paystack_access_code: string;
  paid_at: string | null;
  created_at: string;
}

export interface Rating {
  id: number;
  service_request: number;
  client: number;
  serviceman: number;
  rating: number;
  review: string;
  created_at: string;
}

export interface Notification {
  id: number;
  user: number;
  notification_type: string;
  title: string;
  message: string;
  service_request: number | null;
  is_read: boolean;
  sent_to_email: boolean;
  email_sent_at: string | null;
  created_at: string;
}

export interface PriceNegotiation {
  id: number;
  service_request: number;
  proposed_by: User;
  proposed_amount: string;
  message: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COUNTERED';
  created_at: string;
}
```

---

## 🔍 Search & Filter Examples

### Complex Servicemen Search
```javascript
function ServicemenSearch() {
  const [filters, setFilters] = useState({
    category: '',
    is_available: '',
    min_rating: '',
    search: '',
    ordering: '-rating'
  });
  
  const searchServicemen = async () => {
    const data = await API.getAllServicemen(filters);
    return data.results;
  };
  
  return (
    <div>
      <input 
        placeholder="Search name..."
        value={filters.search}
        onChange={(e) => setFilters({...filters, search: e.target.value})}
      />
      
      <select onChange={(e) => setFilters({...filters, category: e.target.value})}>
        <option value="">All Categories</option>
        <option value="1">Plumbing</option>
        <option value="2">Electrical</option>
      </select>
      
      <select onChange={(e) => setFilters({...filters, is_available: e.target.value})}>
        <option value="">All</option>
        <option value="true">Available Only</option>
        <option value="false">Busy Only</option>
      </select>
      
      <select onChange={(e) => setFilters({...filters, min_rating: e.target.value})}>
        <option value="">Any Rating</option>
        <option value="4.0">4+ Stars</option>
        <option value="4.5">4.5+ Stars</option>
      </select>
      
      <button onClick={searchServicemen}>Search</button>
    </div>
  );
}
```

---

## 🎨 React Hooks

### useServicemen Hook
```typescript
import { useState, useEffect } from 'react';

interface ServicemenFilters {
  category?: number;
  is_available?: boolean;
  min_rating?: number;
  search?: string;
  ordering?: string;
}

function useServicemen(filters: ServicemenFilters = {}) {
  const [servicemen, setServicemen] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    setLoading(true);
    API.getAllServicemen(filters)
      .then(async response => {
        const data = await response.json();
        setServicemen(data.results);
        setStatistics(data.statistics);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, [JSON.stringify(filters)]);
  
  return { servicemen, statistics, loading, error };
}

// Usage
function ServicemenList() {
  const { servicemen, statistics, loading } = useServicemen({
    is_available: true,
    min_rating: 4.0
  });
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>Available Servicemen ({statistics.available})</h2>
      {servicemen.map(s => <ServicemanCard key={s.user} data={s} />)}
    </div>
  );
}
```

### useNotifications Hook
```typescript
function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const loadNotifications = async () => {
    const [notifs, countData] = await Promise.all([
      API.getNotifications().then(r => r.json()),
      API.getUnreadCount().then(r => r.json())
    ]);
    
    setNotifications(notifs);
    setUnreadCount(countData.unread_count);
    setLoading(false);
  };
  
  const markAsRead = async (id: number) => {
    await API.markAsRead(id);
    await loadNotifications();
  };
  
  const markAllRead = async () => {
    await API.markAllRead();
    await loadNotifications();
  };
  
  useEffect(() => {
    loadNotifications();
    
    // Poll every 30 seconds
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllRead,
    reload: loadNotifications
  };
}
```

---

## 🧪 Testing

### Automated Test Example
```javascript
import { describe, it, expect } from '@jest/globals';
import API from './services/api';

describe('ServiceMan API', () => {
  let adminToken;
  let clientToken;
  
  beforeAll(async () => {
    // Get admin token
    const adminLogin = await API.login('admin', 'password');
    const adminData = await adminLogin.json();
    adminToken = adminData.access;
    
    // Get client token
    const clientLogin = await API.login('client', 'password');
    const clientData = await clientLogin.json();
    clientToken = clientData.access;
  });
  
  it('should list all servicemen', async () => {
    const response = await fetch('/api/users/servicemen/');
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data).toHaveProperty('statistics');
    expect(data).toHaveProperty('results');
    expect(Array.isArray(data.results)).toBe(true);
  });
  
  it('should get pending servicemen (admin only)', async () => {
    const response = await fetch('/api/users/admin/pending-servicemen/', {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    
    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty('total_pending');
  });
  
  it('should create service request (client)', async () => {
    const response = await fetch('/api/service-requests/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${clientToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category_id: 1,
        booking_date: '2025-10-25',
        client_address: '123 Test St',
        service_description: 'Test service'
      })
    });
    
    expect(response.status).toBe(201);
  });
});
```

---

## 📞 Interactive Documentation

**Best for live testing and examples:**

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🎁 Additional Resources

### Code Repositories
- Backend examples: All view files in `apps/*/views.py`
- Frontend examples: `FRONTEND_API_CONSUMPTION_GUIDE.md`

### Postman Collection
Import from: `http://localhost:8000/api/schema/`

### Quick References
- `ADMIN_ENDPOINTS_QUICK_REFERENCE.md` - Admin endpoints
- `CLIENT_ENDPOINTS_QUICK_START.md` - Client endpoints
- `API_ENDPOINTS_VISUAL_MAP.md` - Visual map

---

## ✅ Summary

**Total Endpoints**: 50+  
**Public Endpoints**: 15  
**Authenticated Endpoints**: 25  
**Admin-Only Endpoints**: 10  

**Authentication**: JWT-based  
**Response Format**: JSON  
**Base URL**: http://localhost:8000 (dev), https://serviceman-backend.onrender.com (prod)  

**Status**: ✅ Production Ready  
**Documentation**: ✅ Complete  
**Examples**: ✅ Provided  

---

**Version**: 2.0.0  
**Last Updated**: October 2025  
**Maintained by**: ServiceMan Platform Backend Team


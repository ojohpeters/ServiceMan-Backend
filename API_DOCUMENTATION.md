# Serviceman Platform API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format
All responses are in JSON format. Success responses include the requested data, while error responses include a `detail` field with the error message.

---

## 🔐 Authentication Endpoints

### Register User
**POST** `/users/register/`

**Authentication:** Not required

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "user_type": "CLIENT"
}
```

**Response (201):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "user_type": "CLIENT",
    "is_email_verified": false
}
```

### Login
**POST** `/users/token/`

**Authentication:** Not required

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
**POST** `/users/token/refresh/`

**Authentication:** Not required

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Verify Email
**GET** `/users/verify-email/?uid=123&token=abc123`

**Authentication:** Not required

**Response (200):**
```json
{
    "detail": "Email verified."
}
```

### Resend Verification Email
**POST** `/users/resend-verification-email/`

**Authentication:** Not required

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

**Response (200):**
```json
{
    "detail": "Verification email sent."
}
```

### Password Reset Request
**POST** `/users/password-reset/`

**Authentication:** Not required

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

### Password Reset Confirm
**POST** `/users/password-reset-confirm/?uid=123&token=abc123`

**Authentication:** Not required

**Request Body:**
```json
{
    "password": "NewSecurePass123!"
}
```

---

## 👤 User Profile Endpoints

### Get Current User
**GET** `/users/me/`

**Authentication:** Required

**Response (200):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "user_type": "CLIENT",
    "is_email_verified": true
}
```

### Get/Update Client Profile
**GET/PUT** `/users/client-profile/`

**Authentication:** Required (Client only)

**Response (200):**
```json
{
    "user": 1,
    "phone_number": "+2348012345678",
    "address": "123 Main St, Lagos",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get/Update Serviceman Profile
**GET/PUT** `/users/serviceman-profile/`

**Authentication:** Required (Serviceman only)

**Response (200):**
```json
{
    "user": 2,
    "category": 1,
    "rating": 4.8,
    "total_jobs_completed": 45,
    "bio": "Experienced electrician with 10+ years...",
    "years_of_experience": 10,
    "phone_number": "+2348012345678",
    "is_available": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Public Serviceman Profile
**GET** `/users/servicemen/{user_id}/`

**Authentication:** Not required

**Response (200):**
```json
{
    "user": 2,
    "category": 1,
    "rating": 4.8,
    "total_jobs_completed": 45,
    "bio": "Experienced electrician with 10+ years...",
    "years_of_experience": 10,
    "phone_number": "+2348012345678",
    "is_available": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 🏷️ Categories Endpoints

### List Categories
**GET** `/services/categories/`

**Authentication:** Not required

**Response (200):**
```json
[
    {
        "id": 1,
        "name": "Electrical",
        "description": "Electrical services and repairs",
        "icon_url": "https://example.com/electrical.png",
        "is_active": true
    },
    {
        "id": 2,
        "name": "Plumbing",
        "description": "Plumbing services and repairs",
        "icon_url": "https://example.com/plumbing.png",
        "is_active": true
    }
]
```

### Get Servicemen by Category
**GET** `/services/categories/{category_id}/servicemen/`

**Authentication:** Not required

**Response (200):**
```json
[
    {
        "id": 2,
        "full_name": "John Smith",
        "rating": 4.8,
        "total_jobs_completed": 45,
        "bio": "Experienced electrician with 10+ years...",
        "years_of_experience": 10
    },
    {
        "id": 3,
        "full_name": "Jane Doe",
        "rating": 4.5,
        "total_jobs_completed": 32,
        "bio": "Professional electrician specializing in...",
        "years_of_experience": 8
    }
]
```

### Create Category (Admin Only)
**POST** `/services/categories/`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
    "name": "HVAC",
    "description": "Heating, Ventilation, and Air Conditioning",
    "icon_url": "https://example.com/hvac.png"
}
```

### Update Category (Admin Only)
**PUT/PATCH** `/services/categories/{category_id}/`

**Authentication:** Required (Admin only)

---

## 📋 Service Requests Endpoints

### Create Service Request
**POST** `/services/service-requests/`

**Authentication:** Required (Client only)

**Request Body:**
```json
{
    "serviceman": 2,
    "category": 1,
    "booking_date": "2024-01-15T10:00:00Z",
    "is_emergency": false,
    "address": "123 Main St, Lagos",
    "description": "Need electrical repair for faulty outlet"
}
```

**Response (201):**
```json
{
    "id": 1,
    "client": 1,
    "serviceman": 2,
    "category": 1,
    "status": "PENDING_PAYMENT",
    "booking_date": "2024-01-15T10:00:00Z",
    "is_emergency": false,
    "address": "123 Main St, Lagos",
    "description": "Need electrical repair for faulty outlet",
    "initial_fee": 2000.00,
    "created_at": "2024-01-01T00:00:00Z"
}
```

### List Service Requests
**GET** `/services/service-requests/`

**Authentication:** Required

**Response (200):**
```json
[
    {
        "id": 1,
        "client": 1,
        "serviceman": 2,
        "category": 1,
        "status": "ASSIGNED_TO_SERVICEMAN",
        "booking_date": "2024-01-15T10:00:00Z",
        "is_emergency": false,
        "address": "123 Main St, Lagos",
        "description": "Need electrical repair for faulty outlet",
        "initial_fee": 2000.00,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### Get Service Request Details
**GET** `/services/service-requests/{request_id}/`

**Authentication:** Required (Owner, assigned serviceman, or admin)

**Response (200):**
```json
{
    "id": 1,
    "client": 1,
    "serviceman": 2,
    "category": 1,
    "status": "ASSIGNED_TO_SERVICEMAN",
    "booking_date": "2024-01-15T10:00:00Z",
    "is_emergency": false,
    "address": "123 Main St, Lagos",
    "description": "Need electrical repair for faulty outlet",
    "initial_fee": 2000.00,
    "serviceman_estimated_cost": 15000.00,
    "final_cost": 18000.00,
    "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 💳 Payment Endpoints

### Initialize Payment
**POST** `/payments/initialize/`

**Authentication:** Required

**Request Body:**
```json
{
    "service_request_id": 1,
    "amount": 2000.00,
    "email": "client@example.com"
}
```

**Response (201):**
```json
{
    "authorization_url": "https://checkout.paystack.com/abc123",
    "access_code": "abc123",
    "reference": "T1234567890"
}
```

### Verify Payment
**GET** `/payments/verify/?reference=T1234567890`

**Authentication:** Not required

**Response (200):**
```json
{
    "status": "success",
    "message": "Payment verified successfully",
    "data": {
        "reference": "T1234567890",
        "amount": 2000.00,
        "status": "success"
    }
}
```

---

## 💬 Negotiation Endpoints

### List Negotiations
**GET** `/negotiations/`

**Authentication:** Required

**Query Parameters:**
- `request_id` (optional): Filter by service request ID

**Response (200):**
```json
[
    {
        "id": 1,
        "service_request": 1,
        "initiator": 1,
        "message": "The cost seems high, can we negotiate?",
        "status": "PENDING",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### Create Negotiation
**POST** `/negotiations/create/`

**Authentication:** Required

**Request Body:**
```json
{
    "service_request": 1,
    "message": "The cost seems high, can we negotiate?"
}
```

### Accept Negotiation
**POST** `/negotiations/{negotiation_id}/accept/`

**Authentication:** Required

### Counter Negotiation
**POST** `/negotiations/{negotiation_id}/counter/`

**Authentication:** Required

**Request Body:**
```json
{
    "message": "I can offer 15,000 instead of 18,000"
}
```

---

## 🔔 Notification Endpoints

### List Notifications
**GET** `/notifications/`

**Authentication:** Required

**Response (200):**
```json
[
    {
        "id": 1,
        "user": 1,
        "title": "Service Request Assigned",
        "message": "Your service request has been assigned to John Smith",
        "is_read": false,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### Get Unread Count
**GET** `/notifications/unread-count/`

**Authentication:** Required

**Response (200):**
```json
{
    "unread_count": 3
}
```

### Mark Notification as Read
**PATCH** `/notifications/{notification_id}/read/`

**Authentication:** Required

### Mark All Notifications as Read
**PATCH** `/notifications/mark-all-read/`

**Authentication:** Required

---

## ⭐ Rating Endpoints

### List Ratings
**GET** `/ratings/`

**Authentication:** Not required

**Query Parameters:**
- `serviceman_id` (optional): Filter by serviceman ID

**Response (200):**
```json
[
    {
        "id": 1,
        "service_request": 1,
        "client": 1,
        "serviceman": 2,
        "rating": 5,
        "review": "Excellent work! Very professional and timely.",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### Create Rating
**POST** `/ratings/create/`

**Authentication:** Required (Client only)

**Request Body:**
```json
{
    "service_request": 1,
    "rating": 5,
    "review": "Excellent work! Very professional and timely."
}
```

---

## 📊 Analytics Endpoints (Admin Only)

### Revenue Analytics
**GET** `/ratings/analytics/revenue/`

**Authentication:** Required (Admin only)

**Response (200):**
```json
{
    "total_revenue": 150000.00,
    "this_month": 25000.00
}
```

### Top Servicemen Analytics
**GET** `/ratings/analytics/servicemen/`

**Authentication:** Required (Admin only)

**Response (200):**
```json
[
    {
        "id": 2,
        "full_name": "John Smith",
        "rating": 4.8,
        "total_jobs_completed": 45
    },
    {
        "id": 3,
        "full_name": "Jane Doe",
        "rating": 4.5,
        "total_jobs_completed": 32
    }
]
```

### Top Categories Analytics
**GET** `/ratings/analytics/categories/`

**Authentication:** Required (Admin only)

**Response (200):**
```json
[
    {
        "id": 1,
        "name": "Electrical",
        "request_count": 150
    },
    {
        "id": 2,
        "name": "Plumbing",
        "request_count": 120
    }
]
```

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
    "detail": "Invalid input data."
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "A server error occurred."
}
```

---

## 📝 Status Codes Reference

### Service Request Statuses
- `PENDING_PAYMENT` - Initial payment required
- `PAYMENT_CONFIRMED` - Payment received, awaiting assignment
- `ASSIGNED_TO_SERVICEMAN` - Assigned to serviceman
- `SERVICEMAN_INSPECTED` - Serviceman has inspected and provided estimate
- `NEGOTIATION_PENDING` - Cost negotiation in progress
- `NEGOTIATION_ACCEPTED` - Negotiation accepted, work can proceed
- `IN_PROGRESS` - Work is in progress
- `COMPLETED` - Work completed
- `CANCELLED` - Request cancelled

### User Types
- `CLIENT` - Service requester
- `SERVICEMAN` - Service provider
- `ADMIN` - Platform administrator

### Payment Statuses
- `PENDING` - Payment initiated
- `SUCCESSFUL` - Payment completed
- `FAILED` - Payment failed
- `CANCELLED` - Payment cancelled

---

## 🔧 Frontend Integration Examples

### JavaScript/React Examples

#### Authentication
```javascript
// Login
const login = async (username, password) => {
    const response = await fetch('/api/users/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data;
};

// Make authenticated request
const makeAuthenticatedRequest = async (url, options = {}) => {
    const token = localStorage.getItem('access_token');
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
};
```

#### Browse Categories and Servicemen
```javascript
// Get categories
const getCategories = async () => {
    const response = await fetch('/api/services/categories/');
    return response.json();
};

// Get servicemen by category
const getServicemenByCategory = async (categoryId) => {
    const response = await fetch(`/api/services/categories/${categoryId}/servicemen/`);
    return response.json();
};

// Get serviceman profile
const getServicemanProfile = async (userId) => {
    const response = await fetch(`/api/users/servicemen/${userId}/`);
    return response.json();
};
```

#### Create Service Request
```javascript
const createServiceRequest = async (requestData) => {
    const response = await makeAuthenticatedRequest('/api/services/service-requests/', {
        method: 'POST',
        body: JSON.stringify(requestData)
    });
    return response.json();
};
```

#### Initialize Payment
```javascript
const initializePayment = async (serviceRequestId, amount, email) => {
    const response = await makeAuthenticatedRequest('/api/payments/initialize/', {
        method: 'POST',
        body: JSON.stringify({
            service_request_id: serviceRequestId,
            amount: amount,
            email: email
        })
    });
    const data = await response.json();
    // Redirect to Paystack
    window.location.href = data.authorization_url;
};
```

---

## 🎯 Quick Reference

### Public Endpoints (No Auth Required)
- `GET /api/services/categories/`
- `GET /api/services/categories/{id}/servicemen/`
- `GET /api/users/servicemen/{user_id}/`
- `GET /api/ratings/`
- `POST /api/users/register/`
- `POST /api/users/token/`
- `GET /api/users/verify-email/`
- `POST /api/users/resend-verification-email/`

### Client-Only Endpoints
- `POST /api/services/service-requests/`
- `POST /api/ratings/create/`

### Serviceman-Only Endpoints
- `GET/PUT /api/users/serviceman-profile/`

### Admin-Only Endpoints
- `POST /api/services/categories/`
- `PUT/PATCH /api/services/categories/{id}/`
- `GET /api/ratings/analytics/*`

### Authenticated Endpoints (All Roles)
- `GET /api/users/me/`
- `GET /api/services/service-requests/`
- `GET /api/services/service-requests/{id}/`
- `GET /api/notifications/`
- `GET /api/negotiations/`

---

This documentation covers all available endpoints in the Serviceman Platform API. For the most up-to-date schema information, visit `/api/docs/` for the interactive Swagger documentation.

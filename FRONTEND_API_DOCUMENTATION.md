# 📚 ServiceMan Backend API - Complete Frontend Documentation

**Version:** 2.1  
**Last Updated:** November 5, 2025  
**Base URL:** `https://your-api-domain.com/api`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [User Management](#user-management-endpoints)
   - [Service Categories](#service-categories-endpoints)
   - [Servicemen](#servicemen-endpoints)
   - [Service Requests](#service-requests-endpoints)
   - [Payments](#payments-endpoints)
   - [Notifications](#notifications-endpoints)
   - [Skills](#skills-endpoints)
   - [Admin](#admin-endpoints)
6. [Service Request Workflow](#service-request-workflow)
7. [Payment Integration](#payment-integration)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## 🎯 Overview

ServiceMan is a comprehensive service marketplace platform connecting clients with skilled service providers. This API powers:

- **Client Features:** Book services, track requests, make payments, leave reviews
- **Serviceman Features:** Receive assignments, submit estimates, complete jobs, earn ratings
- **Admin Features:** Manage users, assign jobs, approve servicemen, oversee workflow

### Key Features

✅ **JWT Authentication** - Secure token-based auth  
✅ **Role-Based Access** - CLIENT, SERVICEMAN, ADMIN roles  
✅ **Professional Workflow** - 8-step service request lifecycle  
✅ **Paystack Integration** - Booking fees & final payments  
✅ **Real-time Notifications** - In-app notifications for all actions  
✅ **Skills Management** - Categorized service skills  
✅ **Serviceman Approval** - Admin approval workflow  
✅ **Availability Tracking** - Real-time serviceman availability

---

## 🔐 Authentication

### Authentication Flow

```
1. Register → 2. Verify Email → 3. Login → 4. Use Access Token → 5. Refresh Token
```

### Token Types

- **Access Token:** Short-lived (15 min), included in all requests
- **Refresh Token:** Long-lived (7 days), used to get new access tokens

### Authentication Header

```http
Authorization: Bearer <access_token>
```

---

## 🚀 Quick Start

### 1. Register a New User

```javascript
const response = await fetch('https://api.example.com/api/users/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_plumber',
    email: 'john@example.com',
    password: 'SecurePass123!',
    user_type: 'SERVICEMAN',  // or 'CLIENT'
    skill_ids: [1, 3, 5]  // For servicemen only
  })
});
```

**Response:**
```json
{
  "id": 42,
  "username": "john_plumber",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "message": "Registration successful. Please check your email to verify your account."
}
```

### 2. Login

```javascript
const response = await fetch('https://api.example.com/api/users/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_plumber',
    password: 'SecurePass123!'
  })
});

const { access, refresh, user } = await response.json();
localStorage.setItem('accessToken', access);
localStorage.setItem('refreshToken', refresh);
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 42,
    "username": "john_plumber",
    "email": "john@example.com",
    "user_type": "SERVICEMAN",
    "is_email_verified": true
  }
}
```

### 3. Make Authenticated Request

```javascript
const accessToken = localStorage.getItem('accessToken');

const response = await fetch('https://api.example.com/api/users/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

---

## 🧠 Core Concepts

### User Types

| Type | Description | Key Features |
|------|-------------|--------------|
| **CLIENT** | End users who book services | Book services, make payments, leave reviews |
| **SERVICEMAN** | Service providers | Receive jobs, submit estimates, complete work |
| **ADMIN** | Platform administrators | Manage users, assign jobs, approve servicemen |

### Service Request States

The service request lifecycle has 8 main states:

```
1. PENDING_ADMIN_ASSIGNMENT → Client creates request
2. PENDING_ESTIMATION → Admin assigns serviceman
3. ESTIMATION_SUBMITTED → Serviceman submits estimate
4. AWAITING_CLIENT_APPROVAL → Admin finalizes price
5. PAYMENT_COMPLETED → Client pays
6. IN_PROGRESS → Admin authorizes work
7. COMPLETED → Serviceman completes job
8. CLIENT_REVIEWED → Client leaves review
```

### Notification Types

All workflow transitions trigger notifications:

- `SERVICE_REQUEST_CREATED` - New request notification to admin
- `SERVICE_REQUEST_ASSIGNED` - Assignment notification to serviceman
- `ESTIMATE_SUBMITTED` - Estimate ready for admin review
- `PRICE_FINALIZED` - Payment request to client
- `PAYMENT_COMPLETED` - Payment confirmation
- `WORK_AUTHORIZED` - Work authorization to serviceman
- `JOB_COMPLETED` - Completion notification to admin/client
- `COMPLETION_CONFIRMED` - Final confirmation
- `REVIEW_SUBMITTED` - New review notification

---

## 📡 API Endpoints

### Authentication Endpoints

#### POST `/api/users/register/`
Register a new user (Client or Serviceman).

**Public Endpoint** - No authentication required

**Request Body:**
```json
{
  "username": "string (required, 3-150 chars)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "user_type": "CLIENT | SERVICEMAN (required)",
  "skill_ids": [1, 2, 3]  // Optional, for servicemen only
}
```

**Response (201):**
```json
{
  "id": 42,
  "username": "john_plumber",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "message": "Registration successful. Please check your email to verify your account."
}
```

**Errors:**
- `400` - Validation error (username/email exists, weak password, etc.)
- `500` - Server error

---

#### POST `/api/users/login/`
Login with username/email and password.

**Public Endpoint**

**Request Body:**
```json
{
  "username": "john_plumber",  // or email
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 42,
    "username": "john_plumber",
    "email": "john@example.com",
    "user_type": "SERVICEMAN",
    "is_email_verified": true
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `400` - Missing username/password

---

#### POST `/api/users/token/refresh/`
Refresh access token using refresh token.

**Public Endpoint**

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors:**
- `401` - Invalid or expired refresh token

---

#### GET `/api/users/verify-email/?uid=<uid>&token=<token>`
Verify user email address.

**Public Endpoint**

**Query Parameters:**
- `uid` - User ID from verification email
- `token` - Verification token from email

**Response (200):**
```json
{
  "detail": "Email verified successfully."
}
```

**Errors:**
- `400` - Invalid or expired token
- `404` - User not found

---

#### POST `/api/users/resend-verification-email/`
Resend email verification link.

**Public Endpoint**

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "detail": "If the email exists, a verification link has been sent."
}
```

**Security Note:** Returns generic message to prevent email enumeration attacks.

---

#### POST `/api/users/password-reset/`
Request a password reset link via email.

**Public Endpoint** - No authentication required

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "detail": "If the email exists in our system, a password reset link has been sent."
}
```

**Features:**
- 🔒 **Secure:** Generic response prevents email enumeration
- ⏰ **Expires:** Reset link expires after 24 hours
- 📧 **Beautiful Email:** HTML email with branded template
- 🎯 **Single Use:** Token can only be used once

**Email Template Includes:**
- Reset password button
- Direct link (if button doesn't work)
- Security tips
- Warning if user didn't request reset

---

#### POST `/api/users/password-reset-confirm/?uid=<uid>&token=<token>`
Confirm password reset and set new password.

**Public Endpoint** - No authentication required

**Query Parameters:**
- `uid` - User ID from reset email
- `token` - Reset token from email

**Request Body:**
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

**Response (400):**
```json
{
  "detail": "Invalid or expired token."
}
```

**Validation Rules:**
- Minimum 8 characters
- Token expires after 24 hours
- Token is single-use only

**After Success:**
- ✅ Password is updated
- ✅ User receives confirmation email
- ✅ User can login with new password
- ⚠️ All active sessions remain valid (user should re-login)

---

### 📧 Email Verification & Password Reset - Complete Guide

#### 🎯 Email Verification Flow

**1. User Registers**
```javascript
// Frontend: User submits registration form
const response = await fetch('/api/users/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'SecurePass123!',
    user_type: 'CLIENT'
  })
});

if (response.ok) {
  // Show success message
  alert('Registration successful! Please check your email to verify your account.');
  // Redirect to "check your email" page
  window.location.href = '/check-email';
}
```

**2. Backend Sends Verification Email**

The backend automatically:
- ✅ Creates user account
- ✅ Generates secure verification token
- ✅ Sends beautiful HTML email with verification link
- ✅ Link format: `http://your-frontend.com/verify-email?uid=42&token=abc123...`

**3. User Clicks Email Link**
```javascript
// Frontend: Parse URL parameters and verify
const urlParams = new URLSearchParams(window.location.search);
const uid = urlParams.get('uid');
const token = urlParams.get('token');

// Call verification endpoint
const response = await fetch(`/api/users/verify-email/?uid=${uid}&token=${token}`, {
  method: 'GET'
});

const data = await response.json();

if (response.ok) {
  alert('Email verified successfully! You can now login.');
  window.location.href = '/login';
} else {
  alert('Verification failed: ' + data.detail);
}
```

**4. Resend Verification Email (if needed)**
```javascript
// Frontend: If user didn't receive email
const response = await fetch('/api/users/resend-verification-email/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com'
  })
});

if (response.ok) {
  alert('Verification email resent! Please check your inbox.');
}
```

---

#### 🔐 Password Reset Flow

**1. User Requests Password Reset**
```javascript
// Frontend: User enters email on forgot password page
const response = await fetch('/api/users/password-reset/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com'
  })
});

const data = await response.json();
alert(data.detail); // Always shows generic message for security
window.location.href = '/check-email-reset';
```

**2. Backend Sends Reset Email**

The backend automatically:
- ✅ Generates secure reset token (expires in 24 hours)
- ✅ Sends beautiful HTML email with reset link
- ✅ Link format: `http://your-frontend.com/reset-password?uid=42&token=xyz789...`
- ⚠️ If email doesn't exist, still returns success (security)

**3. User Clicks Reset Link**
```javascript
// Frontend: Show password reset form
// Parse URL parameters
const urlParams = new URLSearchParams(window.location.search);
const uid = urlParams.get('uid');
const token = urlParams.get('token');

// User enters new password
document.getElementById('resetForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const newPassword = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  if (newPassword !== confirmPassword) {
    alert('Passwords do not match!');
    return;
  }
  
  if (newPassword.length < 8) {
    alert('Password must be at least 8 characters!');
    return;
  }
  
  // Submit password reset
  const response = await fetch(`/api/users/password-reset-confirm/?uid=${uid}&token=${token}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      password: newPassword
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    alert('Password reset successful! You can now login.');
    window.location.href = '/login';
  } else {
    alert('Reset failed: ' + data.detail);
  }
});
```

**4. User Receives Confirmation Email**

After successful reset:
- ✅ Password is updated in database
- ✅ User receives "password changed" confirmation email
- ✅ User can login with new password

---

#### 🎨 Frontend Components (React Example)

**Email Verification Page**
```jsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const uid = searchParams.get('uid');
      const token = searchParams.get('token');

      if (!uid || !token) {
        setStatus('error');
        setMessage('Invalid verification link.');
        return;
      }

      try {
        const response = await fetch(
          `/api/users/verify-email/?uid=${uid}&token=${token}`
        );
        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage('Email verified successfully!');
          setTimeout(() => navigate('/login'), 2000);
        } else {
          setStatus('error');
          setMessage(data.detail || 'Verification failed.');
        }
      } catch (error) {
        setStatus('error');
        setMessage('Network error. Please try again.');
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  return (
    <div className="verify-email-container">
      {status === 'verifying' && (
        <div className="spinner">Verifying your email...</div>
      )}
      {status === 'success' && (
        <div className="success">
          <h2>✅ {message}</h2>
          <p>Redirecting to login...</p>
        </div>
      )}
      {status === 'error' && (
        <div className="error">
          <h2>❌ {message}</h2>
          <button onClick={() => navigate('/resend-verification')}>
            Resend Verification Email
          </button>
        </div>
      )}
    </div>
  );
}
```

**Forgot Password Page**
```jsx
import { useState } from 'react';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/users/password-reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        setSent(true);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="check-email">
        <h2>📧 Check Your Email</h2>
        <p>
          If an account exists for <strong>{email}</strong>, 
          you will receive a password reset link shortly.
        </p>
        <p>Please check your inbox and spam folder.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="forgot-password-form">
      <h2>🔐 Forgot Password?</h2>
      <p>Enter your email and we'll send you a reset link.</p>
      
      <input
        type="email"
        placeholder="your@email.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Reset Link'}
      </button>
    </form>
  );
}
```

**Reset Password Page**
```jsx
import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match!');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    const uid = searchParams.get('uid');
    const token = searchParams.get('token');

    if (!uid || !token) {
      setError('Invalid reset link.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `/api/users/password-reset-confirm/?uid=${uid}&token=${token}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert('✅ Password reset successful!');
        navigate('/login');
      } else {
        setError(data.detail || 'Reset failed. Please try again.');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="reset-password-form">
      <h2>🔑 Set New Password</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <input
        type="password"
        placeholder="New Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <ul className="password-requirements">
        <li className={password.length >= 8 ? 'valid' : ''}>
          At least 8 characters
        </li>
        <li className={password === confirmPassword && password ? 'valid' : ''}>
          Passwords match
        </li>
      </ul>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Resetting...' : 'Reset Password'}
      </button>
    </form>
  );
}
```

---

#### 🛠️ Email Configuration (Backend)

**Required Environment Variables:**
```env
# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # or your SMTP host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ServiceMan Platform <noreply@servicemanplatform.com>

# Frontend URL (for email links)
FRONTEND_URL=https://your-frontend.com
```

**Email Templates Included:**
- ✅ `email_verification.html` - Beautiful verification email
- ✅ `password_reset.html` - Password reset request email
- ✅ `password_reset_success.html` - Password changed confirmation
- ✅ `base.html` - Base template with branding

---

#### ✅ Frontend Checklist

**Email Verification:**
- [ ] Create `/verify-email` route
- [ ] Parse `uid` and `token` from URL
- [ ] Call verification endpoint
- [ ] Show success/error message
- [ ] Redirect to login on success
- [ ] Add "Resend email" option for errors

**Password Reset:**
- [ ] Create `/forgot-password` page with email form
- [ ] Create `/reset-password` route
- [ ] Parse `uid` and `token` from URL
- [ ] Add password strength indicator
- [ ] Validate password match
- [ ] Show success message and redirect
- [ ] Handle expired token error

**UX Enhancements:**
- [ ] Add loading states
- [ ] Show password requirements
- [ ] Add "Check spam folder" reminder
- [ ] Link to support if issues persist
- [ ] Add countdown timer for redirects

---

### User Management Endpoints

#### GET `/api/users/profile/`
Get current user's profile.

**Authentication:** Required

**Response (200):**
```json
{
  "id": 42,
  "username": "john_plumber",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": true,
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-11-01T10:00:00Z"
}
```

---

#### GET `/api/users/<id>/`
Get user details by ID.

**Authentication:** Required  
**Permissions:** Admin or viewing own profile

**Response (200):**
```json
{
  "id": 42,
  "username": "john_plumber",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": true
}
```

---

#### GET `/api/users/client-profile/`
Get client profile details.

**Authentication:** Required (CLIENT only)

**Response (200):**
```json
{
  "user": 42,
  "phone_number": "+1234567890",
  "address": "123 Main St, City",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z"
}
```

---

#### PATCH `/api/users/client-profile/`
Update client profile.

**Authentication:** Required (CLIENT only)

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "address": "456 Oak Ave, City"
}
```

**Response (200):** Updated profile object

---

#### GET `/api/users/serviceman-profile/`
Get serviceman profile details.

**Authentication:** Required (SERVICEMAN only)

**Response (200):**
```json
{
  "id": 10,
  "user": {
    "id": 42,
    "username": "john_plumber",
    "email": "john@example.com",
    "full_name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "SERVICEMAN",
    "is_email_verified": true
  },
  "category": {
    "id": 1,
    "name": "Plumbing",
    "icon": "🔧"
  },
  "skills": [
    {
      "id": 1,
      "name": "Pipe Repair",
      "category": 1,
      "description": "Fix leaking pipes",
      "is_active": true
    }
  ],
  "rating": 4.5,
  "total_jobs_completed": 23,
  "bio": "Experienced plumber with 10 years...",
  "years_of_experience": 10,
  "phone_number": "+1234567890",
  "is_available": true,
  "active_jobs_count": 2,
  "availability_status": {
    "status": "busy",
    "label": "Currently Busy",
    "message": "This serviceman is currently working on 2 job(s)...",
    "can_book": true,
    "active_jobs": 2,
    "warning": "Booking a busy serviceman may result in delayed service..."
  },
  "is_approved": true,
  "approved_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  "approved_at": "2025-11-01T12:00:00Z",
  "rejection_reason": "",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-04T14:30:00Z"
}
```

---

#### PATCH `/api/users/serviceman-profile/`
Update serviceman profile.

**Authentication:** Required (SERVICEMAN only)

**Request Body:**
```json
{
  "bio": "Updated bio text...",
  "years_of_experience": 12,
  "phone_number": "+1234567890",
  "is_available": false,
  "skill_ids": [1, 3, 5, 7]
}
```

**Response (200):** Updated profile object

---

### Service Categories Endpoints

#### GET `/api/services/categories/`
Get all service categories.

**Public Endpoint**

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Plumbing",
      "description": "Plumbing services including pipe repair...",
      "icon": "🔧",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

#### GET `/api/services/categories/<id>/`
Get category details with available servicemen.

**Public Endpoint**

**Response (200):**
```json
{
  "id": 1,
  "name": "Plumbing",
  "description": "Plumbing services...",
  "icon": "🔧",
  "servicemen_count": 12,
  "available_servicemen": 8
}
```

---

#### GET `/api/services/categories/<id>/servicemen/`
Get all servicemen in a category.

**Public Endpoint**

**Response (200):**
```json
{
  "category": {
    "id": 1,
    "name": "Plumbing",
    "description": "Plumbing services..."
  },
  "total_servicemen": 12,
  "available_servicemen": 8,
  "servicemen": [
    {
      "id": 42,
      "username": "john_plumber",
      "full_name": "John Doe",
      "rating": 4.5,
      "total_jobs_completed": 23,
      "is_available": true,
      "availability_status": {
        "status": "available",
        "label": "Available",
        "can_book": true
      }
    }
  ]
}
```

---

### Servicemen Endpoints

#### GET `/api/users/servicemen/`
Get all approved servicemen with filtering & search.

**Public Endpoint**

**Query Parameters:**
- `category` - Filter by category ID
- `is_available` - Filter by availability (true/false)
- `min_rating` - Filter by minimum rating (0-5)
- `search` - Search by name, username, or email
- `ordering` - Sort by: rating, total_jobs_completed, years_of_experience, created_at (prefix with `-` for descending)

**Example:**
```
GET /api/users/servicemen/?category=1&is_available=true&min_rating=4.0&ordering=-rating
```

**Response (200):**
```json
{
  "count": 15,
  "statistics": {
    "total_servicemen": 15,
    "available_servicemen": 10,
    "busy_servicemen": 5
  },
  "results": [
    {
      "id": 10,
      "user": 42,
      "category": 1,
      "skills": [...],
      "rating": 4.8,
      "total_jobs_completed": 45,
      "bio": "...",
      "years_of_experience": 15,
      "phone_number": "+1234567890",
      "is_available": true,
      "active_jobs_count": 0,
      "availability_status": {...}
    }
  ]
}
```

---

#### GET `/api/users/servicemen/<id>/`
Get serviceman details by ID.

**Public Endpoint**

**Response (200):** Full serviceman profile object (same as `/api/users/serviceman-profile/`)

---

#### GET `/api/services/serviceman/job-history/`
Get job history for authenticated serviceman.

**Authentication:** Required (SERVICEMAN only)

**Query Parameters:**
- `status` - Filter by status (e.g., COMPLETED, IN_PROGRESS)
- `from_date` - Filter jobs from date (YYYY-MM-DD)
- `to_date` - Filter jobs to date (YYYY-MM-DD)

**Response (200):**
```json
{
  "serviceman": {
    "id": 42,
    "username": "john_plumber",
    "full_name": "John Doe"
  },
  "statistics": {
    "total_jobs": 50,
    "completed_jobs": 45,
    "in_progress_jobs": 2,
    "pending_estimation": 3,
    "average_rating": 4.7,
    "total_earnings": "45000.00"
  },
  "jobs": [
    {
      "id": 123,
      "client": {
        "id": 5,
        "username": "client_user",
        "email": "client@example.com"
      },
      "category": {
        "id": 1,
        "name": "Plumbing"
      },
      "description": "Fix kitchen sink leak",
      "status": "COMPLETED",
      "created_at": "2025-10-15T10:00:00Z",
      "completed_at": "2025-10-16T15:30:00Z",
      "final_price": "250.00",
      "client_rating": 5,
      "client_review": "Excellent work!"
    }
  ]
}
```

---

### Service Requests Endpoints

#### GET `/api/services/service-requests/`
Get all service requests (filtered by role).

**Authentication:** Required

**Behavior by Role:**
- **CLIENT:** Returns only their own service requests
- **SERVICEMAN:** Returns requests assigned to them
- **ADMIN:** Returns all service requests

**Query Parameters:**
- `status` - Filter by status
- `category` - Filter by category ID
- `is_emergency` - Filter emergency requests (true/false)

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 123,
      "client": {
        "id": 5,
        "username": "client_user",
        "email": "client@example.com"
      },
      "serviceman": {
        "id": 42,
        "username": "john_plumber",
        "full_name": "John Doe"
      },
      "category": {
        "id": 1,
        "name": "Plumbing"
      },
      "description": "Kitchen sink is leaking badly",
      "location": "123 Main St, Apt 4B",
      "is_emergency": true,
      "status": "IN_PROGRESS",
      "estimated_price": "300.00",
      "final_price": "300.00",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-02T14:30:00Z"
    }
  ]
}
```

---

#### POST `/api/services/service-requests/`
Create a new service request.

**Authentication:** Required (CLIENT only)

**Request Body:**
```json
{
  "category": 1,
  "description": "Kitchen sink is leaking under the counter. Water dripping continuously.",
  "location": "123 Main St, Apt 4B, New York, NY 10001",
  "preferred_date": "2025-11-10",  // Optional
  "preferred_time": "14:00:00",    // Optional
  "is_emergency": true,            // Required for booking fee calculation
  "images": ["base64_image_1", "base64_image_2"]  // Optional
}
```

**Response (201):**
```json
{
  "id": 123,
  "client": 5,
  "category": 1,
  "description": "Kitchen sink is leaking...",
  "location": "123 Main St...",
  "is_emergency": true,
  "status": "PENDING_ADMIN_ASSIGNMENT",
  "created_at": "2025-11-04T10:00:00Z",
  "message": "Service request created. Admin will assign a serviceman soon."
}
```

**Notifications Sent:**
- Admin receives `SERVICE_REQUEST_CREATED` notification
- Client receives confirmation notification

**Errors:**
- `400` - Validation error (missing fields, invalid category)
- `401` - Not authenticated
- `403` - Not a client user

---

#### GET `/api/services/service-requests/<id>/`
Get service request details.

**Authentication:** Required

**Permissions:**
- **CLIENT:** Can view own requests
- **SERVICEMAN:** Can view assigned requests
- **ADMIN:** Can view all requests

**Response (200):** Full service request object with all details

---

#### PATCH `/api/services/service-requests/<id>/`
Update service request (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "status": "CANCELLED",
  "admin_notes": "Cancelled per client request"
}
```

**Response (200):** Updated service request object

---

#### POST `/api/services/service-requests/<id>/assign/`
Assign serviceman to request (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "serviceman_id": 42,
  "backup_serviceman_id": 43,  // Optional
  "admin_notes": "Assigned based on availability and rating"
}
```

**Response (200):**
```json
{
  "message": "Service request assigned successfully",
  "service_request": {
    "id": 123,
    "serviceman": {...},
    "backup_serviceman": {...},
    "status": "PENDING_ESTIMATION"
  }
}
```

**Notifications Sent:**
- Primary serviceman: `SERVICE_REQUEST_ASSIGNED`
- Backup serviceman: `SERVICE_REQUEST_ASSIGNED` (as backup)
- Client: `SERVICE_REQUEST_ASSIGNED` (with serviceman info)

---

#### POST `/api/services/service-requests/<id>/submit-estimate/`
Submit price estimate (Serviceman only).

**Authentication:** Required (SERVICEMAN only)

**Request Body:**
```json
{
  "estimated_price": 350.00,
  "estimated_completion_days": 1,
  "notes": "Need to replace valve and reseal connections. Materials included."
}
```

**Response (200):**
```json
{
  "message": "Estimate submitted successfully",
  "service_request": {
    "id": 123,
    "estimated_price": "350.00",
    "status": "ESTIMATION_SUBMITTED"
  }
}
```

**Notifications Sent:**
- Admin: `ESTIMATE_SUBMITTED`
- Client: `ESTIMATE_SUBMITTED` (informational)

---

#### POST `/api/services/service-requests/<id>/finalize-price/`
Finalize service price (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "final_price": 300.00,
  "admin_notes": "Negotiated price. Materials confirmed available."
}
```

**Response (200):**
```json
{
  "message": "Price finalized successfully",
  "service_request": {
    "id": 123,
    "final_price": "300.00",
    "status": "AWAITING_CLIENT_APPROVAL"
  }
}
```

**Notifications Sent:**
- Client: `PRICE_FINALIZED` (with payment instructions)
- Serviceman: `PRICE_FINALIZED` (informational)

---

#### POST `/api/services/service-requests/<id>/authorize-work/`
Authorize serviceman to start work (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "admin_notes": "Payment verified. Serviceman authorized to proceed."
}
```

**Response (200):**
```json
{
  "message": "Work authorized successfully",
  "service_request": {
    "id": 123,
    "status": "IN_PROGRESS"
  }
}
```

**Notifications Sent:**
- Serviceman: `WORK_AUTHORIZED`
- Client: `WORK_AUTHORIZED`

---

#### POST `/api/services/service-requests/<id>/complete-job/`
Mark job as completed (Serviceman only).

**Authentication:** Required (SERVICEMAN only)

**Request Body:**
```json
{
  "completion_notes": "Replaced faulty valve, resealed all connections. Tested for 30 minutes. No leaks detected.",
  "completion_images": ["base64_image_1", "base64_image_2"]  // Optional
}
```

**Response (200):**
```json
{
  "message": "Job marked as completed",
  "service_request": {
    "id": 123,
    "status": "COMPLETED"
  }
}
```

**Notifications Sent:**
- Admin: `JOB_COMPLETED`
- Client: `JOB_COMPLETED`

---

#### POST `/api/services/service-requests/<id>/confirm-completion/`
Confirm job completion (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "admin_notes": "Verified completion with client. Quality confirmed."
}
```

**Response (200):**
```json
{
  "message": "Completion confirmed successfully",
  "service_request": {
    "id": 123,
    "status": "COMPLETED"
  }
}
```

**Notifications Sent:**
- Serviceman: `COMPLETION_CONFIRMED`
- Client: `COMPLETION_CONFIRMED`

---

#### POST `/api/services/service-requests/<id>/submit-review/`
Submit client review and rating (Client only).

**Authentication:** Required (CLIENT only)

**Request Body:**
```json
{
  "rating": 5,
  "review": "Excellent work! Very professional and fixed the issue quickly. Highly recommend!"
}
```

**Response (200):**
```json
{
  "message": "Review submitted successfully",
  "service_request": {
    "id": 123,
    "client_rating": 5,
    "client_review": "Excellent work!...",
    "status": "CLIENT_REVIEWED"
  }
}
```

**Notifications Sent:**
- Serviceman: `REVIEW_SUBMITTED` (with rating/review)
- Admin: `REVIEW_SUBMITTED` (informational)

**Effects:**
- Updates serviceman's average rating
- Increments serviceman's total jobs completed count

---

### Payments Endpoints

#### POST `/api/payments/initialize-booking-fee/`
Initialize booking fee payment (before service request creation).

**Authentication:** Required (CLIENT only)

**Request Body:**
```json
{
  "is_emergency": true,  // true = 5000, false = 2000
  "email": "client@example.com"
}
```

**Response (200):**
```json
{
  "authorization_url": "https://checkout.paystack.com/abc123",
  "access_code": "abc123xyz",
  "reference": "BOOK-1699123456-ABC123",
  "amount": 5000,  // In currency's smallest unit (kobo for NGN)
  "message": "Please complete payment to proceed with booking"
}
```

**Frontend Action:** Redirect user to `authorization_url` to complete payment

---

#### POST `/api/payments/initialize/`
Initialize final service payment.

**Authentication:** Required (CLIENT only)

**Request Body:**
```json
{
  "service_request_id": 123,
  "email": "client@example.com"
}
```

**Response (200):**
```json
{
  "authorization_url": "https://checkout.paystack.com/xyz789",
  "access_code": "xyz789abc",
  "reference": "PAY-1699123456-XYZ789",
  "amount": 30000,  // final_price * 100
  "message": "Please complete payment"
}
```

---

#### GET `/api/payments/verify/?reference=<reference>`
Verify payment status (webhook callback).

**Public Endpoint** (but should only be called by Paystack webhook or after payment redirect)

**Query Parameters:**
- `reference` - Payment reference from initialization

**Response (200):**
```json
{
  "status": "success",
  "message": "Payment verified successfully",
  "payment": {
    "id": 45,
    "reference": "PAY-1699123456-XYZ789",
    "amount": "300.00",
    "status": "completed",
    "service_request": 123,
    "created_at": "2025-11-04T10:00:00Z"
  }
}
```

**For Booking Fee Payments:**
- No service request yet, so `service_request` will be `null`
- Client should now create service request

**For Final Payments:**
- Updates service request status to `PAYMENT_COMPLETED`
- Sends notifications to admin and client

---

#### GET `/api/payments/history/`
Get payment history for current user.

**Authentication:** Required

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 45,
      "service_request": {
        "id": 123,
        "description": "Kitchen sink leak"
      },
      "amount": "300.00",
      "reference": "PAY-1699123456-XYZ789",
      "status": "completed",
      "is_emergency": true,
      "created_at": "2025-11-04T10:00:00Z"
    }
  ]
}
```

---

### Notifications Endpoints

#### GET `/api/notifications/`
Get notifications for current user.

**Authentication:** Required

**Query Parameters:**
- `is_read` - Filter by read status (true/false)
- `notification_type` - Filter by type
- `limit` - Results per page (default: 20)

**Response (200):**
```json
{
  "count": 15,
  "unread_count": 5,
  "results": [
    {
      "id": 78,
      "user": 42,
      "notification_type": "SERVICE_REQUEST_ASSIGNED",
      "title": "New Job Assignment",
      "message": "You have been assigned to service request #123: Kitchen sink leak",
      "data": {
        "service_request_id": 123,
        "client_id": 5,
        "is_backup": false
      },
      "is_read": false,
      "created_at": "2025-11-04T10:00:00Z"
    }
  ]
}
```

---

#### POST `/api/notifications/<id>/mark-read/`
Mark notification as read.

**Authentication:** Required

**Response (200):**
```json
{
  "message": "Notification marked as read",
  "notification": {
    "id": 78,
    "is_read": true
  }
}
```

---

#### POST `/api/notifications/mark-all-read/`
Mark all notifications as read.

**Authentication:** Required

**Response (200):**
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

---

### Skills Endpoints

#### GET `/api/users/skills/`
Get all active skills.

**Public Endpoint**

**Query Parameters:**
- `category` - Filter by category ID
- `search` - Search by skill name

**Response (200):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "name": "Pipe Repair",
      "category": 1,
      "description": "Repair and replace damaged pipes",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

#### POST `/api/users/skills/` (Admin Only)
Create a new skill.

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "name": "Solar Panel Installation",
  "category": 3,
  "description": "Install and maintain solar panel systems"
}
```

**Response (201):** Created skill object

---

#### GET `/api/users/servicemen/<id>/skills/`
Get skills for a specific serviceman.

**Public Endpoint**

**Response (200):**
```json
{
  "serviceman": {
    "id": 42,
    "username": "john_plumber",
    "full_name": "John Doe"
  },
  "skills": [
    {
      "id": 1,
      "name": "Pipe Repair",
      "category": 1,
      "description": "Repair and replace damaged pipes"
    }
  ]
}
```

---

#### PUT `/api/users/servicemen/<id>/skills/`
Update serviceman's skills (Serviceman or Admin only).

**Authentication:** Required (SERVICEMAN viewing self, or ADMIN)

**Request Body:**
```json
{
  "skill_ids": [1, 3, 5, 7]
}
```

**Response (200):**
```json
{
  "message": "Skills updated successfully",
  "skills": [...]
}
```

---

### Admin Endpoints

#### GET `/api/users/admin/pending-servicemen/`
Get pending serviceman applications (Admin only).

**Authentication:** Required (ADMIN only)

**✅ OPTIMIZED:** Uses `select_related()` and `prefetch_related()` to eliminate N+1 queries

**Query Parameters:**
- `category` - Filter by category ID
- `search` - Search by username, email, or name
- `ordering` - Sort by created_at, username, email (default: created_at)

**Response (200):**
```json
{
  "total_pending": 5,
  "pending_applications": [
    {
      "id": 10,
      "user": {
        "id": 42,
        "username": "john_plumber",
        "email": "john@example.com",
        "full_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "SERVICEMAN",
        "is_email_verified": true
      },
      "category": {
        "id": 1,
        "name": "Plumbing",
        "icon": "🔧"
      },
      "skills": [...],
      "rating": 0.0,
      "total_jobs_completed": 0,
      "bio": "Experienced plumber...",
      "years_of_experience": 10,
      "phone_number": "+1234567890",
      "is_available": true,
      "is_approved": false,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "meta": {
    "query_optimization": "✅ Optimized with select_related() and prefetch_related()",
    "total_queries": "~2-3 queries regardless of result count (no N+1)"
  }
}
```

---

#### POST `/api/users/admin/approve-serviceman/`
Approve a serviceman application (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "serviceman_id": 42,
  "category_id": 1,  // Optional - assign category during approval
  "notes": "Verified credentials. Approved for plumbing services."
}
```

**Response (200):**
```json
{
  "message": "Serviceman approved successfully",
  "serviceman": {
    "id": 10,
    "user": {...},
    "is_approved": true,
    "approved_by": {...},
    "approved_at": "2025-11-04T14:30:00Z"
  }
}
```

**Notifications Sent:**
- Serviceman: `SERVICEMAN_APPROVED` (welcome message)

---

#### POST `/api/users/admin/reject-serviceman/`
Reject a serviceman application (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "serviceman_id": 42,
  "reason": "Incomplete documentation. Please submit valid certifications."
}
```

**Response (200):**
```json
{
  "message": "Serviceman application rejected",
  "serviceman": {
    "id": 10,
    "is_approved": false,
    "rejection_reason": "Incomplete documentation..."
  }
}
```

**Notifications Sent:**
- Serviceman: `SERVICEMAN_REJECTED` (with reason)

---

#### GET `/api/users/admin/servicemen-by-category/`
Get servicemen grouped by category (Admin only).

**Authentication:** Required (ADMIN only)

**Response (200):**
```json
{
  "total_servicemen": 42,
  "categories": [
    {
      "category": {
        "id": 1,
        "name": "Plumbing",
        "description": "Plumbing services"
      },
      "servicemen_count": 12,
      "servicemen": [
        {
          "id": 42,
          "username": "john_plumber",
          "full_name": "John Doe",
          "email": "john@example.com",
          "is_available": true,
          "is_approved": true,
          "rating": 4.5,
          "total_jobs_completed": 23
        }
      ]
    }
  ]
}
```

---

#### POST `/api/users/admin/create/`
Create a new admin user (Admin only).

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "username": "new_admin",
  "email": "newadmin@example.com",
  "password": "SecureAdminPass123!",
  "password_confirm": "SecureAdminPass123!",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response (201):**
```json
{
  "id": 2,
  "username": "new_admin",
  "email": "newadmin@example.com",
  "user_type": "ADMIN",
  "is_staff": true,
  "is_email_verified": true
}
```

---

## 🔄 Service Request Workflow

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE REQUEST LIFECYCLE                     │
└─────────────────────────────────────────────────────────────────┘

1️⃣ CLIENT CREATES REQUEST
   ├─ POST /api/services/service-requests/
   ├─ Status: PENDING_ADMIN_ASSIGNMENT
   └─ Notification → Admin

2️⃣ ADMIN ASSIGNS SERVICEMAN
   ├─ POST /api/services/service-requests/{id}/assign/
   ├─ Status: PENDING_ESTIMATION
   └─ Notifications → Serviceman, Backup Serviceman, Client

3️⃣ SERVICEMAN SUBMITS ESTIMATE
   ├─ POST /api/services/service-requests/{id}/submit-estimate/
   ├─ Status: ESTIMATION_SUBMITTED
   └─ Notifications → Admin, Client

4️⃣ ADMIN FINALIZES PRICE
   ├─ POST /api/services/service-requests/{id}/finalize-price/
   ├─ Status: AWAITING_CLIENT_APPROVAL
   └─ Notifications → Client (payment link), Serviceman

5️⃣ CLIENT PAYS
   ├─ POST /api/payments/initialize/
   ├─ GET /api/payments/verify/
   ├─ Status: PAYMENT_COMPLETED
   └─ Notifications → Admin, Client

6️⃣ ADMIN AUTHORIZES WORK
   ├─ POST /api/services/service-requests/{id}/authorize-work/
   ├─ Status: IN_PROGRESS
   └─ Notifications → Serviceman, Client

7️⃣ SERVICEMAN COMPLETES JOB
   ├─ POST /api/services/service-requests/{id}/complete-job/
   ├─ Status: COMPLETED
   └─ Notifications → Admin, Client

8️⃣ CLIENT SUBMITS REVIEW
   ├─ POST /api/services/service-requests/{id}/submit-review/
   ├─ Status: CLIENT_REVIEWED
   └─ Notifications → Serviceman, Admin
```

### Status Transition Matrix

| Current Status | Allowed Transitions | Who Can Transition |
|----------------|---------------------|-------------------|
| `PENDING_ADMIN_ASSIGNMENT` | `PENDING_ESTIMATION`, `CANCELLED` | Admin |
| `PENDING_ESTIMATION` | `ESTIMATION_SUBMITTED`, `CANCELLED` | Serviceman, Admin |
| `ESTIMATION_SUBMITTED` | `AWAITING_CLIENT_APPROVAL`, `PENDING_ESTIMATION` | Admin |
| `AWAITING_CLIENT_APPROVAL` | `PAYMENT_COMPLETED`, `CANCELLED` | System (after payment) |
| `PAYMENT_COMPLETED` | `IN_PROGRESS`, `CANCELLED` | Admin |
| `IN_PROGRESS` | `COMPLETED`, `CANCELLED` | Serviceman, Admin |
| `COMPLETED` | `CLIENT_REVIEWED` | Client |
| `CLIENT_REVIEWED` | - | Final state |
| `CANCELLED` | - | Final state |

---

## 💳 Payment Integration

### Booking Fee Payment Flow

```javascript
// 1. Initialize booking fee payment
const initResponse = await fetch('/api/payments/initialize-booking-fee/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    is_emergency: true,  // 5000 NGN for emergency, 2000 NGN for normal
    email: 'client@example.com'
  })
});

const { authorization_url, reference } = await initResponse.json();

// 2. Redirect to Paystack
window.location.href = authorization_url;

// 3. After payment, Paystack redirects back to your callback URL
// Verify payment
const verifyResponse = await fetch(`/api/payments/verify/?reference=${reference}`);
const result = await verifyResponse.json();

if (result.status === 'success') {
  // 4. Now create the service request
  const requestResponse = await fetch('/api/services/service-requests/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      category: 1,
      description: 'Kitchen sink leak...',
      location: '123 Main St...',
      is_emergency: true
    })
  });
}
```

### Final Payment Flow

```javascript
// 1. After price is finalized, initialize payment
const initResponse = await fetch('/api/payments/initialize/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_request_id: 123,
    email: 'client@example.com'
  })
});

const { authorization_url, reference } = await initResponse.json();

// 2. Redirect to Paystack
window.location.href = authorization_url;

// 3. After payment, verify (automatic via webhook + manual check)
const verifyResponse = await fetch(`/api/payments/verify/?reference=${reference}`);
const result = await verifyResponse.json();

if (result.status === 'success') {
  // Service request status automatically updated to PAYMENT_COMPLETED
  // Notifications sent to admin and client
  console.log('Payment successful! Service will proceed.');
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | When to Show |
|------|---------|-------------|
| `200` | Success | Request succeeded |
| `201` | Created | Resource created |
| `400` | Bad Request | Validation errors, show specific error messages |
| `401` | Unauthorized | Token expired/invalid, redirect to login |
| `403` | Forbidden | User doesn't have permission |
| `404` | Not Found | Resource doesn't exist |
| `500` | Server Error | Backend issue, show generic error |
| `503` | Service Unavailable | Maintenance/migrations in progress |

### Error Response Format

```json
{
  "error": "Validation error",
  "detail": "Description of what went wrong",
  "field_errors": {
    "email": ["This email is already registered"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

### Error Handling Example

```javascript
async function apiRequest(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (response.status === 401) {
      // Try to refresh token
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry original request with new token
        return apiRequest(url, options);
      } else {
        // Redirect to login
        window.location.href = '/login';
        return;
      }
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'An error occurred');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // Show user-friendly error message
    showErrorToast(error.message);
    throw error;
  }
}
```

### Token Refresh Implementation

```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    return false;
  }
  
  try {
    const response = await fetch('/api/users/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (!response.ok) {
      return false;
    }
    
    const { access, refresh } = await response.json();
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    
    return true;
  } catch (error) {
    return false;
  }
}
```

---

## 🎯 Best Practices

### 1. Token Management

✅ **DO:**
- Store tokens in localStorage or secure cookies
- Implement automatic token refresh
- Clear tokens on logout
- Handle 401 errors globally

❌ **DON'T:**
- Store tokens in plain URL parameters
- Keep tokens after logout
- Ignore token expiration

### 2. API Request Optimization

✅ **DO:**
- Cache GET requests when appropriate
- Use query parameters for filtering
- Implement pagination for large lists
- Debounce search inputs

❌ **DON'T:**
- Fetch the same data repeatedly
- Load all data without pagination
- Make API calls on every keystroke

### 3. Error Display

✅ **DO:**
- Show user-friendly error messages
- Provide actionable feedback
- Log errors for debugging
- Handle network failures gracefully

❌ **DON'T:**
- Show raw API errors to users
- Ignore errors silently
- Show generic "Error occurred" for everything

### 4. Notification Handling

✅ **DO:**
- Poll `/api/notifications/` every 30-60 seconds for new notifications
- Show unread count in UI
- Provide notification center/dropdown
- Mark notifications as read when viewed

❌ **DON'T:**
- Poll too frequently (wastes resources)
- Ignore notification types
- Auto-mark all as read

### 5. State Management

✅ **DO:**
- Keep service request status in sync
- Update UI immediately after actions
- Refetch data after mutations
- Show loading states

❌ **DON'T:**
- Assume status without checking
- Show stale data
- Leave UI frozen during requests

### 6. File Uploads

✅ **DO:**
- Validate file types and sizes before upload
- Show upload progress
- Use base64 for images when required
- Compress images before sending

❌ **DON'T:**
- Upload huge files without validation
- Block UI during uploads
- Send raw image data without compression

---

## 📞 Support & Resources

### API Documentation Tools

- **Swagger UI:** `https://your-api-domain.com/api/schema/swagger-ui/`
- **ReDoc:** `https://your-api-domain.com/api/schema/redoc/`
- **OpenAPI Schema:** `https://your-api-domain.com/api/schema/`

### Quick Links

- [Service Request Workflow](#service-request-workflow)
- [Payment Integration](#payment-integration)
- [Error Handling](#error-handling)
- [Authentication](#authentication)

### Common Scenarios

**Scenario 1: Client Books Emergency Service**
1. Pay booking fee (5000 NGN) → `/api/payments/initialize-booking-fee/`
2. Create service request → `/api/services/service-requests/`
3. Wait for admin assignment → Poll `/api/services/service-requests/{id}/`
4. Receive price → Notification `PRICE_FINALIZED`
5. Pay final amount → `/api/payments/initialize/`
6. Track progress → `/api/services/service-requests/{id}/`
7. Submit review → `/api/services/service-requests/{id}/submit-review/`

**Scenario 2: Serviceman Completes Job**
1. Receive assignment → `/api/notifications/`
2. View job details → `/api/services/service-requests/{id}/`
3. Submit estimate → `/api/services/service-requests/{id}/submit-estimate/`
4. Wait for payment → Check status
5. Complete work → `/api/services/service-requests/{id}/complete-job/`
6. Receive review → `/api/notifications/`

**Scenario 3: Admin Manages Workflow**
1. View pending requests → `/api/services/service-requests/?status=PENDING_ADMIN_ASSIGNMENT`
2. Assign serviceman → `/api/services/service-requests/{id}/assign/`
3. Review estimate → Check status `ESTIMATION_SUBMITTED`
4. Finalize price → `/api/services/service-requests/{id}/finalize-price/`
5. Authorize work → `/api/services/service-requests/{id}/authorize-work/`
6. Confirm completion → `/api/services/service-requests/{id}/confirm-completion/`

---

## 🔧 Testing Examples

### React/Next.js Example

```javascript
// hooks/useServiceRequests.js
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export function useServiceRequests(status = null) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRequests() {
      try {
        const params = status ? `?status=${status}` : '';
        const data = await apiClient.get(`/services/service-requests/${params}`);
        setRequests(data.results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchRequests();
  }, [status]);

  return { requests, loading, error };
}

// Usage in component
function ServiceRequestsList() {
  const { requests, loading, error } = useServiceRequests('PENDING_ESTIMATION');

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;

  return (
    <div>
      {requests.map(request => (
        <ServiceRequestCard key={request.id} request={request} />
      ))}
    </div>
  );
}
```

### Vue.js Example

```javascript
// composables/useNotifications.js
import { ref, onMounted, onUnmounted } from 'vue';
import { api } from '@/services/api';

export function useNotifications() {
  const notifications = ref([]);
  const unreadCount = ref(0);
  let pollInterval = null;

  async function fetchNotifications() {
    try {
      const data = await api.get('/notifications/');
      notifications.value = data.results;
      unreadCount.value = data.unread_count;
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }

  async function markAsRead(notificationId) {
    try {
      await api.post(`/notifications/${notificationId}/mark-read/`);
      await fetchNotifications(); // Refresh
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  }

  onMounted(() => {
    fetchNotifications();
    // Poll every 30 seconds
    pollInterval = setInterval(fetchNotifications, 30000);
  });

  onUnmounted(() => {
    if (pollInterval) {
      clearInterval(pollInterval);
    }
  });

  return {
    notifications,
    unreadCount,
    markAsRead,
    refresh: fetchNotifications
  };
}
```

---

## 🎉 Changelog

### Version 2.0 (November 4, 2025)

**🚀 Major Updates:**

1. **Backend Query Optimization**
   - ✅ Eliminated N+1 query problem in admin endpoints
   - ✅ Added `select_related()` for user, category, approved_by
   - ✅ Added `prefetch_related()` for skills
   - ✅ 90% performance improvement (2-3 queries vs N+1)

2. **Enhanced API Responses**
   - ✅ Full user objects in serviceman profiles (no more ID-only responses)
   - ✅ Nested user data includes: id, username, email, full_name, first_name, last_name
   - ✅ Category objects include: id, name, icon
   - ✅ Skills fully expanded in responses

3. **New Serializers**
   - ✅ `UserBasicSerializer` - Lightweight nested user data
   - ✅ `AdminServicemanProfileSerializer` - Optimized for admin endpoints

4. **Updated Endpoints**
   - ✅ `/api/users/admin/pending-servicemen/` - Now returns full user objects
   - ✅ `/api/users/servicemen/` - Optimized with select_related
   - ✅ Added filtering and search to pending servicemen endpoint

**Previous Updates:**
- Professional 8-step workflow implementation
- Paystack payment integration
- Real-time notifications system
- Skills management system
- Serviceman approval workflow

---

## 📄 License

This API is proprietary and confidential. Unauthorized use is prohibited.

---

**Need Help?**  
Contact the backend team or refer to the interactive API documentation at `/api/schema/swagger-ui/`



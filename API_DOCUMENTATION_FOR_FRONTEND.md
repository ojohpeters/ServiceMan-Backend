# 🚀 ServiceMan API Documentation - Frontend Integration Guide

**Last Updated**: November 2025  
**API Version**: 1.0  
**Base URL**: `https://serviceman-backend.onrender.com`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [New Workflow Endpoints](#new-workflow-endpoints)
4. [Complete Workflow Example](#complete-workflow-example)
5. [Status Reference](#status-reference)
6. [Notification Types](#notification-types)
7. [Error Handling](#error-handling)
8. [Frontend Implementation Examples](#frontend-implementation-examples)

---

## 🎯 Overview

### What Changed?

We've implemented a **complete professional workflow system** with the following key features:

✨ **9-Step Workflow**: From booking to review with admin oversight  
🔔 **Automatic Notifications**: Every action triggers relevant notifications  
👨‍💼 **Admin as Bridge**: All communication flows through admin  
📞 **Phone Integration**: Serviceman gets client phone for direct calls  
⭐ **Rating System**: 5-star ratings with optional reviews  

### New Endpoints Summary

| Endpoint | Role | Purpose |
|----------|------|---------|
| `POST /api/services/service-requests/{id}/submit-estimate/` | Serviceman | Submit cost estimate |
| `POST /api/services/service-requests/{id}/finalize-price/` | Admin | Add platform fee |
| `POST /api/services/service-requests/{id}/authorize-work/` | Admin | Start the job |
| `POST /api/services/service-requests/{id}/complete-job/` | Serviceman | Mark as done |
| `POST /api/services/service-requests/{id}/confirm-completion/` | Admin | Confirm to client |
| `POST /api/services/service-requests/{id}/submit-review/` | Client | Rate serviceman |

---

## 🔐 Authentication

All endpoints require authentication via JWT tokens.

### Headers Required:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

### Getting Tokens:

```javascript
// Login
const response = await fetch('https://serviceman-backend.onrender.com/api/users/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});

const { access, refresh } = await response.json();
// Store tokens in localStorage/secure storage
```

---

## 📡 New Workflow Endpoints

### 1. Submit Cost Estimate (Serviceman Only)

**Endpoint**: `POST /api/services/service-requests/{id}/submit-estimate/`

**When to Use**: After serviceman completes site visit and wants to submit cost estimate

**Required Status**: `PENDING_ESTIMATION`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/submit-estimate/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      estimated_cost: 25000.00,
      notes: "Includes parts replacement and 2 days labor" // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Estimate submitted successfully. Admin will review and finalize pricing.",
  "service_request": {
    "id": 123,
    "status": "ESTIMATION_SUBMITTED",
    "serviceman_estimated_cost": "25000.00",
    "category": {
      "id": 2,
      "name": "Plumbing"
    },
    "booking_date": "2025-11-10",
    "client": {
      "id": 45,
      "email": "client@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

**Errors**:
```json
// 403 - Not the assigned serviceman
{
  "error": "You are not assigned to this service request"
}

// 400 - Wrong status
{
  "error": "Cannot submit estimate. Current status: ESTIMATION_SUBMITTED"
}

// 400 - Invalid cost
{
  "error": "Invalid estimated_cost: Cost must be positive"
}
```

**Notifications Triggered**:
- ✅ **Admin**: "Cost Estimate Submitted - Review and add platform fee"

---

### 2. Finalize Price (Admin Only)

**Endpoint**: `POST /api/services/service-requests/{id}/finalize-price/`

**When to Use**: After reviewing serviceman's estimate, admin adds platform fee

**Required Status**: `ESTIMATION_SUBMITTED`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/finalize-price/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      markup_percentage: 10.00, // Optional, defaults to 10%
      admin_notes: "Price includes all materials and labor" // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Price finalized and sent to client for approval",
  "service_request": {
    "id": 123,
    "status": "AWAITING_CLIENT_APPROVAL",
    "serviceman_estimated_cost": "25000.00",
    "admin_markup_percentage": "10.00",
    "final_cost": "27500.00"
  },
  "pricing_breakdown": {
    "base_cost": 25000.00,
    "platform_fee": 2500.00,
    "markup_percentage": 10.00,
    "final_cost": 27500.00
  }
}
```

**Errors**:
```json
// 403 - Not admin
{
  "error": "Only administrators can finalize pricing"
}

// 400 - Wrong status
{
  "error": "Cannot finalize price. Current status: AWAITING_CLIENT_APPROVAL"
}

// 400 - Invalid markup
{
  "error": "Invalid markup_percentage: Markup must be between 0 and 100"
}
```

**Notifications Triggered**:
- ✅ **Client**: "Price Ready - Total: ₦27,500. Please review and pay."

---

### 3. Authorize Work (Admin Only)

**Endpoint**: `POST /api/services/service-requests/{id}/authorize-work/`

**When to Use**: After client has paid, admin authorizes serviceman to begin work

**Required Status**: `PAYMENT_COMPLETED`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/authorize-work/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      instructions: "Client available weekdays 9am-5pm" // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Work authorized. Serviceman has been notified to begin.",
  "service_request": {
    "id": 123,
    "status": "IN_PROGRESS",
    "final_cost": "27500.00",
    "serviceman": {
      "id": 15,
      "email": "serviceman@example.com",
      "first_name": "Mike",
      "last_name": "Smith"
    }
  }
}
```

**Errors**:
```json
// 403 - Not admin
{
  "error": "Only administrators can authorize work"
}

// 400 - Wrong status
{
  "error": "Cannot authorize work. Current status: IN_PROGRESS"
}

// 400 - No serviceman
{
  "error": "No serviceman assigned"
}
```

**Notifications Triggered**:
- ✅ **Serviceman**: "Work Authorized - Begin work. Client: Name, Phone, Address"
- ✅ **Client**: "Work Has Begun - Serviceman will contact you"

---

### 4. Complete Job (Serviceman Only)

**Endpoint**: `POST /api/services/service-requests/{id}/complete-job/`

**When to Use**: When serviceman finishes the work

**Required Status**: `IN_PROGRESS`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/complete-job/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      completion_notes: "All pipes repaired and tested. No leaks." // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Job marked as complete. Admin will verify and notify the client.",
  "service_request": {
    "id": 123,
    "status": "COMPLETED",
    "work_completed_at": "2025-11-15T14:30:00Z"
  }
}
```

**Errors**:
```json
// 403 - Not the assigned serviceman
{
  "error": "You are not assigned to this service request"
}

// 400 - Wrong status
{
  "error": "Cannot mark as complete. Current status: COMPLETED"
}
```

**Notifications Triggered**:
- ✅ **Admin**: "Job Completed - Verify and notify client"

**Side Effects**:
- Serviceman's `total_jobs_completed` counter incremented by 1

---

### 5. Confirm Completion (Admin Only)

**Endpoint**: `POST /api/services/service-requests/{id}/confirm-completion/`

**When to Use**: After verifying job is done, admin notifies client

**Required Status**: `COMPLETED`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/confirm-completion/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message_to_client: "Work verified. Please check and rate." // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Client has been notified of job completion",
  "service_request": {
    "id": 123,
    "status": "COMPLETED",
    "work_completed_at": "2025-11-15T14:30:00Z"
  }
}
```

**Errors**:
```json
// 403 - Not admin
{
  "error": "Only administrators can confirm completion"
}

// 400 - Wrong status
{
  "error": "Cannot confirm completion. Current status: CLIENT_REVIEWED"
}
```

**Notifications Triggered**:
- ✅ **Client**: "Job Completed - Please rate your experience"

---

### 6. Submit Review (Client Only)

**Endpoint**: `POST /api/services/service-requests/{id}/submit-review/`

**When to Use**: After job is complete and admin has confirmed

**Required Status**: `COMPLETED`

**Request**:
```javascript
const response = await fetch(
  `https://serviceman-backend.onrender.com/api/services/service-requests/123/submit-review/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      rating: 5, // Required: 1-5
      review: "Excellent work! Very professional and timely." // Optional
    })
  }
);

const data = await response.json();
```

**Success Response** (200):
```json
{
  "message": "Thank you for your review! Your feedback helps us improve.",
  "service_request": {
    "id": 123,
    "status": "CLIENT_REVIEWED"
  },
  "rating": 5
}
```

**Errors**:
```json
// 403 - Not the client who made the request
{
  "error": "This is not your service request"
}

// 400 - Wrong status
{
  "error": "Cannot submit review. Current status: IN_PROGRESS"
}

// 400 - Invalid rating
{
  "error": "Invalid rating: Rating must be between 1 and 5"
}
```

**Notifications Triggered**:
- ✅ **Serviceman**: "New Review - ⭐⭐⭐⭐⭐ 5-star rating received"
- ✅ **Admin**: "Client Review Submitted - 5/5 stars"

**Side Effects**:
- Serviceman's average rating is recalculated and updated

---

## 🔄 Complete Workflow Example

Here's a complete TypeScript/JavaScript example of the entire workflow:

```typescript
// ========================================
// STEP 1: CLIENT CREATES SERVICE REQUEST
// ========================================

async function createServiceRequest(paymentRef: string) {
  const response = await fetch(
    'https://serviceman-backend.onrender.com/api/services/service-requests/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${clientAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category_id: 2,
        booking_date: '2025-11-10',
        is_emergency: false,
        client_address: '123 Main St, Lagos',
        service_description: 'Leaking pipes in kitchen',
        payment_reference: paymentRef // From booking fee payment
      })
    }
  );
  
  const data = await response.json();
  console.log('Service request created:', data);
  // Status: PENDING_ADMIN_ASSIGNMENT
  // Notifications: Admin + Client
}

// ========================================
// STEP 2: ADMIN ASSIGNS SERVICEMAN
// ========================================

async function assignServiceman(requestId: number, servicemanId: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/assign/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        serviceman_id: servicemanId,
        notes: 'Client prefers morning appointments'
      })
    }
  );
  
  const data = await response.json();
  console.log('Serviceman assigned:', data);
  // Status: PENDING_ESTIMATION
  // Notifications: Serviceman + Client
}

// ========================================
// STEP 3: SERVICEMAN SUBMITS ESTIMATE
// ========================================

async function submitEstimate(requestId: number, cost: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/submit-estimate/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${servicemanAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        estimated_cost: cost,
        notes: 'Includes parts and 2 days labor'
      })
    }
  );
  
  const data = await response.json();
  console.log('Estimate submitted:', data);
  // Status: ESTIMATION_SUBMITTED
  // Notifications: Admin
}

// ========================================
// STEP 4: ADMIN FINALIZES PRICE
// ========================================

async function finalizePrice(requestId: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/finalize-price/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        markup_percentage: 10,
        admin_notes: 'Price includes all materials'
      })
    }
  );
  
  const data = await response.json();
  console.log('Price finalized:', data);
  // Status: AWAITING_CLIENT_APPROVAL
  // Notifications: Client
}

// ========================================
// STEP 5: CLIENT PAYS
// (Payment verification handled by backend)
// ========================================

// After Paystack payment verification:
// Status: PAYMENT_COMPLETED
// Notifications: Admin + Client

// ========================================
// STEP 6: ADMIN AUTHORIZES WORK
// ========================================

async function authorizeWork(requestId: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/authorize-work/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        instructions: 'Client available 9am-5pm'
      })
    }
  );
  
  const data = await response.json();
  console.log('Work authorized:', data);
  // Status: IN_PROGRESS
  // Notifications: Serviceman + Client
}

// ========================================
// STEP 7: SERVICEMAN COMPLETES JOB
// ========================================

async function completeJob(requestId: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/complete-job/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${servicemanAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        completion_notes: 'All repairs done and tested'
      })
    }
  );
  
  const data = await response.json();
  console.log('Job completed:', data);
  // Status: COMPLETED
  // Notifications: Admin
}

// ========================================
// STEP 8: ADMIN CONFIRMS TO CLIENT
// ========================================

async function confirmCompletion(requestId: number) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/confirm-completion/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message_to_client: 'Work verified. Please rate.'
      })
    }
  );
  
  const data = await response.json();
  console.log('Completion confirmed:', data);
  // Status: COMPLETED (awaiting review)
  // Notifications: Client
}

// ========================================
// STEP 9: CLIENT SUBMITS REVIEW
// ========================================

async function submitReview(requestId: number, rating: number, review: string) {
  const response = await fetch(
    `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/submit-review/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${clientAccessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        rating: rating,
        review: review
      })
    }
  );
  
  const data = await response.json();
  console.log('Review submitted:', data);
  // Status: CLIENT_REVIEWED
  // Notifications: Serviceman + Admin
}
```

---

## 📊 Status Reference

### Status Flow:

```
PENDING_ADMIN_ASSIGNMENT
    ↓ (Admin assigns serviceman)
PENDING_ESTIMATION
    ↓ (Serviceman submits estimate)
ESTIMATION_SUBMITTED
    ↓ (Admin finalizes price)
AWAITING_CLIENT_APPROVAL
    ↓ (Client pays)
PAYMENT_COMPLETED
    ↓ (Admin authorizes work)
IN_PROGRESS
    ↓ (Serviceman completes)
COMPLETED
    ↓ (Client reviews)
CLIENT_REVIEWED ✅
```

### Status Descriptions:

| Status | Description | Who Can Act |
|--------|-------------|-------------|
| `PENDING_ADMIN_ASSIGNMENT` | New request waiting for admin | Admin |
| `PENDING_ESTIMATION` | Waiting for serviceman estimate | Serviceman |
| `ESTIMATION_SUBMITTED` | Waiting for admin to add fee | Admin |
| `AWAITING_CLIENT_APPROVAL` | Waiting for client to pay | Client |
| `PAYMENT_COMPLETED` | Waiting for admin authorization | Admin |
| `IN_PROGRESS` | Work is being done | Serviceman |
| `COMPLETED` | Job done, waiting for confirmation | Admin/Client |
| `CLIENT_REVIEWED` | Workflow complete ✅ | - |
| `CANCELLED` | Request cancelled | Admin |

---

## 🔔 Notification Types

Notifications are available at: `GET /api/notifications/`

### Notification Type Values:

```typescript
type NotificationType = 
  | 'GENERAL'              // General information
  | 'ADMIN_ALERT'          // Admin needs to take action
  | 'JOB_ASSIGNED'         // Serviceman assigned to job
  | 'STATUS_UPDATE'        // Request status changed
  | 'PAYMENT_REQUEST'      // Client needs to pay
  | 'PAYMENT_CONFIRMED'    // Payment received
  | 'JOB_COMPLETED'        // Job is done
  | 'REVIEW_RECEIVED';     // New rating/review
```

### Fetching Notifications:

```typescript
async function getNotifications() {
  const response = await fetch(
    'https://serviceman-backend.onrender.com/api/notifications/',
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  const notifications = await response.json();
  return notifications;
}

// Response:
[
  {
    "id": 456,
    "title": "New Job Assignment - Request #123",
    "message": "You have been assigned to a new service request...",
    "notification_type": "JOB_ASSIGNED",
    "is_read": false,
    "created_at": "2025-11-05T10:30:00Z"
  }
]
```

---

## ⚠️ Error Handling

### Common HTTP Status Codes:

| Code | Meaning | Action |
|------|---------|--------|
| `200` | Success | Continue |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Check request data |
| `401` | Unauthorized | Refresh token or login again |
| `403` | Forbidden | User doesn't have permission |
| `404` | Not Found | Resource doesn't exist |
| `500` | Server Error | Contact support |
| `503` | Service Unavailable | Migrations needed (temporary) |

### Error Response Format:

```json
{
  "error": "Short error message",
  "detail": "Detailed explanation of what went wrong"
}
```

### Handling Errors:

```typescript
async function handleRequest(url: string, options: RequestInit) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      // Handle specific errors
      switch (response.status) {
        case 401:
          // Token expired - refresh or redirect to login
          await refreshToken();
          break;
        case 403:
          // Not authorized - show error message
          showError(data.error || 'Not authorized');
          break;
        case 400:
          // Validation error - show to user
          showValidationError(data.detail);
          break;
        case 404:
          // Resource not found
          showError('Request not found');
          break;
        default:
          showError('Something went wrong. Please try again.');
      }
      return null;
    }
    
    return data;
  } catch (error) {
    // Network error
    showError('Network error. Please check your connection.');
    return null;
  }
}
```

---

## 🎨 Frontend Implementation Examples

### React Component Example:

```tsx
import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';

const ServiceRequestCard: React.FC<{ request: ServiceRequest }> = ({ request }) => {
  const { accessToken, user } = useAuth();
  const [loading, setLoading] = useState(false);
  
  const handleSubmitEstimate = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `https://serviceman-backend.onrender.com/api/services/service-requests/${request.id}/submit-estimate/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            estimated_cost: estimateCost,
            notes: estimateNotes
          })
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        showSuccess('Estimate submitted successfully!');
        // Refresh request data
        refreshRequest();
      } else {
        const error = await response.json();
        showError(error.detail || 'Failed to submit estimate');
      }
    } catch (error) {
      showError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Render different UI based on status and user role
  const renderActionButton = () => {
    if (user.user_type === 'SERVICEMAN') {
      if (request.status === 'PENDING_ESTIMATION') {
        return (
          <button onClick={handleSubmitEstimate} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Estimate'}
          </button>
        );
      } else if (request.status === 'IN_PROGRESS') {
        return (
          <button onClick={handleCompleteJob}>
            Mark as Complete
          </button>
        );
      }
    } else if (user.user_type === 'CLIENT') {
      if (request.status === 'AWAITING_CLIENT_APPROVAL') {
        return (
          <button onClick={handlePayment}>
            Pay ₦{request.final_cost}
          </button>
        );
      } else if (request.status === 'COMPLETED') {
        return (
          <button onClick={handleShowReviewModal}>
            Rate Serviceman
          </button>
        );
      }
    } else if (user.user_type === 'ADMIN') {
      // Admin actions based on status
      switch (request.status) {
        case 'PENDING_ADMIN_ASSIGNMENT':
          return <button onClick={handleAssign}>Assign Serviceman</button>;
        case 'ESTIMATION_SUBMITTED':
          return <button onClick={handleFinalizePrice}>Finalize Price</button>;
        case 'PAYMENT_COMPLETED':
          return <button onClick={handleAuthorizeWork}>Authorize Work</button>;
        case 'COMPLETED':
          return <button onClick={handleConfirm}>Confirm to Client</button>;
      }
    }
    
    return null;
  };
  
  return (
    <div className="service-request-card">
      <StatusBadge status={request.status} />
      <h3>Request #{request.id}</h3>
      <p>{request.service_description}</p>
      {renderActionButton()}
    </div>
  );
};
```

### Status Badge Component:

```tsx
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING_ADMIN_ASSIGNMENT':
        return 'bg-yellow-500';
      case 'PENDING_ESTIMATION':
        return 'bg-blue-500';
      case 'ESTIMATION_SUBMITTED':
        return 'bg-orange-500';
      case 'AWAITING_CLIENT_APPROVAL':
        return 'bg-purple-500';
      case 'PAYMENT_COMPLETED':
        return 'bg-green-500';
      case 'IN_PROGRESS':
        return 'bg-green-600';
      case 'COMPLETED':
        return 'bg-blue-600';
      case 'CLIENT_REVIEWED':
        return 'bg-gray-600';
      default:
        return 'bg-gray-400';
    }
  };
  
  const getStatusLabel = (status: string) => {
    return status.replace(/_/g, ' ').toLowerCase()
      .replace(/\b\w/g, l => l.toUpperCase());
  };
  
  return (
    <span className={`status-badge ${getStatusColor(status)}`}>
      {getStatusLabel(status)}
    </span>
  );
};
```

### Review Modal Component:

```tsx
const ReviewModal: React.FC<{ requestId: number, onClose: () => void }> = ({ requestId, onClose }) => {
  const [rating, setRating] = useState(5);
  const [review, setReview] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { accessToken } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await fetch(
        `https://serviceman-backend.onrender.com/api/services/service-requests/${requestId}/submit-review/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ rating, review })
        }
      );
      
      if (response.ok) {
        showSuccess('Thank you for your review!');
        onClose();
      } else {
        const error = await response.json();
        showError(error.detail);
      }
    } catch (error) {
      showError('Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="modal">
      <h2>Rate Your Experience</h2>
      <form onSubmit={handleSubmit}>
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map(star => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              className={rating >= star ? 'star-filled' : 'star-empty'}
            >
              ⭐
            </button>
          ))}
        </div>
        
        <textarea
          placeholder="Tell us about your experience (optional)"
          value={review}
          onChange={(e) => setReview(e.target.value)}
          rows={4}
        />
        
        <div className="modal-actions">
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      </form>
    </div>
  );
};
```

---

## 🚀 Quick Start Checklist

### For Frontend Developers:

- [ ] Update service request detail pages to show new statuses
- [ ] Add action buttons based on user role and current status
- [ ] Implement estimate submission form (Serviceman)
- [ ] Implement price finalization form (Admin)
- [ ] Add work authorization button (Admin)
- [ ] Add job completion button (Serviceman)
- [ ] Add completion confirmation button (Admin)
- [ ] Implement rating/review modal (Client)
- [ ] Update notification handling for new notification types
- [ ] Add status badge component with colors
- [ ] Test complete workflow end-to-end
- [ ] Add error handling for all new endpoints
- [ ] Update loading states and user feedback

---

## 📞 Support

For questions or issues:

1. Check this documentation first
2. Review the detailed workflow guide: `PROFESSIONAL_WORKFLOW_DOCUMENTATION.md`
3. Check quick reference: `WORKFLOW_QUICK_REFERENCE.md`
4. Contact backend team

---

## 🎯 Key Reminders

1. ✅ All endpoints require authentication
2. ✅ Check user role before showing action buttons
3. ✅ Validate status before allowing actions
4. ✅ Handle errors gracefully with user-friendly messages
5. ✅ Show loading states during API calls
6. ✅ Refresh data after successful actions
7. ✅ Display notifications prominently
8. ✅ Use status badges for visual clarity

---

**Happy Coding! 🚀**

*Last Updated: November 2025*

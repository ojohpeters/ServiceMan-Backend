# User-Specific Data Endpoints Documentation

This document provides comprehensive information about all endpoints that return user-specific data, including service requests, notifications, and job history.

## 📋 Table of Contents

1. [Service Requests](#service-requests)
2. [Notifications](#notifications)
3. [Serviceman Job History](#serviceman-job-history)
4. [Authentication](#authentication)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## 🔧 Service Requests

### Get User's Service Requests

**Endpoint:** `GET /api/services/service-requests/`

**Description:** Returns service requests based on user type and permissions.

**Access Control:**
- **Admins:** See all service requests
- **Clients:** See only their own service requests
- **Servicemen:** See requests where they are primary or backup serviceman

**Query Parameters:**
- `status` (optional): Filter by status
- `category` (optional): Filter by category ID
- `is_emergency` (optional): Filter by emergency status (true/false)
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset

**Response Format:**
```json
{
  "count": 25,
  "next": "http://api.example.com/services/service-requests/?limit=10&offset=10",
  "previous": null,
  "results": [
    {
      "id": 123,
      "status": "IN_PROGRESS",
      "status_display": "In Progress",
      "category": {
        "id": 1,
        "name": "Plumbing",
        "description": "Plumbing services"
      },
      "client": {
        "id": 456,
        "username": "john_client",
        "email": "john@example.com",
        "full_name": "John Smith"
      },
      "serviceman": {
        "id": 789,
        "username": "mike_plumber",
        "email": "mike@example.com",
        "full_name": "Mike Johnson"
      },
      "service_description": "Fix leaking faucet",
      "client_address": "123 Main St, City",
      "booking_date": "2025-10-25",
      "is_emergency": false,
      "initial_booking_fee": "2000.00",
      "serviceman_estimated_cost": "5000.00",
      "final_cost": "5500.00",
      "created_at": "2025-10-21T10:30:00Z",
      "inspection_completed_at": "2025-10-22T14:00:00Z",
      "work_completed_at": null
    }
  ]
}
```

**Example Usage:**
```bash
# Get all service requests for current user
GET /api/services/service-requests/

# Get only completed requests
GET /api/services/service-requests/?status=COMPLETED

# Get emergency requests only
GET /api/services/service-requests/?is_emergency=true

# Get requests from specific category
GET /api/services/service-requests/?category=1

# Pagination
GET /api/services/service-requests/?limit=10&offset=20
```

---

## 🔔 Notifications

### Get User's Notifications

**Endpoint:** `GET /api/notifications/`

**Description:** Returns all notifications for the authenticated user, ordered by creation date (newest first).

**Access Control:** Authenticated users only (see their own notifications)

**Query Parameters:**
- `is_read` (optional): Filter by read status (true/false)
- `notification_type` (optional): Filter by notification type
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset

**Response Format:**
```json
{
  "count": 15,
  "next": "http://api.example.com/notifications/?limit=10&offset=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 456,
      "notification_type": "SERVICE_ASSIGNED",
      "title": "New Service Request Assignment",
      "message": "You have been assigned to a new service request #123. Category: Plumbing. Date: 2025-10-25.",
      "service_request": 123,
      "is_read": false,
      "sent_to_email": true,
      "email_sent_at": "2025-10-21T10:30:00Z",
      "created_at": "2025-10-21T10:30:00Z"
    }
  ]
}
```

**Example Usage:**
```bash
# Get all notifications
GET /api/notifications/

# Get only unread notifications
GET /api/notifications/?is_read=false

# Get specific notification type
GET /api/notifications/?notification_type=SERVICE_ASSIGNED

# Pagination
GET /api/notifications/?limit=20&offset=0
```

### Get Unread Notification Count

**Endpoint:** `GET /api/notifications/unread-count/`

**Description:** Returns the count of unread notifications for the authenticated user.

**Response Format:**
```json
{
  "unread_count": 5
}
```

### Mark Notification as Read

**Endpoint:** `PATCH /api/notifications/{id}/read/`

**Description:** Marks a specific notification as read.

**Response Format:**
```json
{
  "detail": "Notification marked as read"
}
```

### Mark All Notifications as Read

**Endpoint:** `POST /api/notifications/mark-all-read/`

**Description:** Marks all notifications for the authenticated user as read.

**Response Format:**
```json
{
  "detail": "All notifications marked as read",
  "updated_count": 5
}
```

---

## 👷 Serviceman Job History

### Get Serviceman Job History

**Endpoint:** `GET /api/services/serviceman/job-history/`

**Description:** Returns comprehensive job history for servicemen, including statistics and performance metrics.

**Access Control:** Servicemen only (see their own job history)

**Query Parameters:**
- `status` (optional): Filter by job status
- `year` (optional): Filter by year
- `month` (optional): Filter by month (1-12)
- `limit` (optional): Number of results (default: 50, max: 100)

**Response Format:**
```json
{
  "serviceman": {
    "id": 789,
    "username": "mike_plumber",
    "email": "mike@example.com",
    "full_name": "Mike Johnson"
  },
  "statistics": {
    "total_jobs": 45,
    "completed_jobs": 38,
    "in_progress_jobs": 3,
    "completion_rate": 84.44,
    "total_earnings": "125000.00",
    "average_job_value": "3289.47"
  },
  "filters_applied": {
    "status": null,
    "year": null,
    "month": null,
    "limit": 50
  },
  "jobs": [
    {
      "id": 123,
      "status": "COMPLETED",
      "status_display": "Completed",
      "category": {
        "id": 1,
        "name": "Plumbing"
      },
      "client": {
        "id": 456,
        "username": "john_client",
        "email": "john@example.com",
        "full_name": "John Smith"
      },
      "service_description": "Fix leaking faucet",
      "client_address": "123 Main St, City",
      "booking_date": "2025-10-25",
      "is_emergency": false,
      "initial_booking_fee": "2000.00",
      "serviceman_estimated_cost": "5000.00",
      "final_cost": "5500.00",
      "created_at": "2025-10-21T10:30:00Z",
      "inspection_completed_at": "2025-10-22T14:00:00Z",
      "work_completed_at": "2025-10-23T16:00:00Z",
      "is_primary_serviceman": true,
      "is_backup_serviceman": false
    }
  ],
  "retrieved_at": "2025-10-21T15:30:00Z"
}
```

**Example Usage:**
```bash
# Get all job history
GET /api/services/serviceman/job-history/

# Get only completed jobs
GET /api/services/serviceman/job-history/?status=COMPLETED

# Get jobs from specific year
GET /api/services/serviceman/job-history/?year=2025

# Get jobs from specific month
GET /api/services/serviceman/job-history/?month=10

# Get jobs from October 2025
GET /api/services/serviceman/job-history/?year=2025&month=10

# Limit results
GET /api/services/serviceman/job-history/?limit=20
```

---

## 🔐 Authentication

All endpoints require authentication using JWT tokens.

**Headers Required:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Getting JWT Token:**
```bash
POST /api/users/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## ❌ Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**400 Bad Request:**
```json
{
  "detail": "Invalid input data.",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

**500 Internal Server Error:**
```json
{
  "detail": "A server error occurred."
}
```

---

## 📝 Examples

### Complete Frontend Integration Example

```javascript
// Service for API calls
class UserDataService {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async getUserServiceRequests(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseURL}/services/service-requests/?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  async getUserNotifications(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseURL}/notifications/?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  async getUnreadCount() {
    const response = await fetch(`${this.baseURL}/notifications/unread-count/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  async getJobHistory(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseURL}/services/serviceman/job-history/?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  async markNotificationRead(notificationId) {
    const response = await fetch(`${this.baseURL}/notifications/${notificationId}/read/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  async markAllNotificationsRead() {
    const response = await fetch(`${this.baseURL}/notifications/mark-all-read/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }
}

// Usage examples
const userService = new UserDataService('https://api.example.com', 'your_jwt_token');

// Get user's service requests
const requests = await userService.getUserServiceRequests({
  status: 'IN_PROGRESS',
  limit: 10
});

// Get unread notifications
const notifications = await userService.getUserNotifications({
  is_read: false
});

// Get unread count
const { unread_count } = await userService.getUnreadCount();

// Get serviceman job history
const jobHistory = await userService.getJobHistory({
  year: 2025,
  month: 10,
  status: 'COMPLETED'
});

// Mark notification as read
await userService.markNotificationRead(123);

// Mark all notifications as read
await userService.markAllNotificationsRead();
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useUserData(token) {
  const [serviceRequests, setServiceRequests] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const [requestsData, notificationsData, unreadData] = await Promise.all([
          fetch('/api/services/service-requests/', {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(res => res.json()),
          fetch('/api/notifications/', {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(res => res.json()),
          fetch('/api/notifications/unread-count/', {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(res => res.json())
        ]);

        setServiceRequests(requestsData.results);
        setNotifications(notificationsData.results);
        setUnreadCount(unreadData.unread_count);
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchUserData();
    }
  }, [token]);

  return {
    serviceRequests,
    notifications,
    unreadCount,
    loading
  };
}
```

---

## 🚀 Quick Reference

| Endpoint | Method | Description | Access |
|----------|--------|-------------|---------|
| `/api/services/service-requests/` | GET | Get user's service requests | Role-based |
| `/api/notifications/` | GET | Get user's notifications | Authenticated |
| `/api/notifications/unread-count/` | GET | Get unread count | Authenticated |
| `/api/notifications/{id}/read/` | PATCH | Mark notification as read | Owner |
| `/api/notifications/mark-all-read/` | POST | Mark all as read | Authenticated |
| `/api/services/serviceman/job-history/` | GET | Get job history | Serviceman only |

---

## 📞 Support

For questions or issues with these endpoints, please contact the development team or check the main API documentation at `/api/docs/`.

---

**Last Updated:** October 21, 2025  
**Version:** 1.0.0

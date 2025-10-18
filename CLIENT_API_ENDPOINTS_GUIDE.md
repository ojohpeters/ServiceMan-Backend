# 📡 Client API Endpoints - Complete Guide

## ✅ All Requested Endpoints Implemented!

This guide covers all 4 endpoints requested by the client, plus additional helpful endpoints.

---

## 🎯 1. GET /users/servicemen/

**List all servicemen for admin assignment**

### Endpoint
```
GET /api/users/servicemen/
```

### Authentication
Required: Yes (Any authenticated user)

### Response
```json
{
  "statistics": {
    "total_servicemen": 25,
    "available": 18,
    "busy": 7
  },
  "results": [
    {
      "user": 1,
      "category": 2,
      "skills": [
        {
          "id": 1,
          "name": "Electrical Wiring",
          "category": "TECHNICAL"
        }
      ],
      "rating": "4.80",
      "total_jobs_completed": 45,
      "bio": "Expert electrician",
      "years_of_experience": 10,
      "phone_number": "+2348012345678",
      "is_available": true,
      "active_jobs_count": 0,
      "availability_status": {
        "status": "available",
        "label": "Available",
        "can_book": true
      }
    }
  ]
}
```

### Filtering Options
```bash
# Filter by category
GET /api/users/servicemen/?category=1

# Only available servicemen
GET /api/users/servicemen/?is_available=true

# Minimum rating
GET /api/users/servicemen/?min_rating=4.5

# Search by name
GET /api/users/servicemen/?search=john

# Sort by rating
GET /api/users/servicemen/?ordering=-rating
```

### Use Case: Admin Assignment
```javascript
// React/JavaScript example
async function getServicemenForAssignment(categoryId) {
  const response = await fetch(
    `/api/users/servicemen/?category=${categoryId}&is_available=true&ordering=-rating`,
    {
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    }
  );
  
  const data = await response.json();
  
  // Show servicemen in dropdown for assignment
  return data.results.map(s => ({
    id: s.user,
    name: `${s.user.username} - Rating: ${s.rating}`,
    available: s.is_available,
    activeJobs: s.active_jobs_count
  }));
}
```

---

## 🎯 2. GET /users/{user_id}/

**Get user details by ID**

### Endpoint
```
GET /api/users/{user_id}/
```

### Authentication
Required: Yes

### Access Control
- ✅ Admins can view any user
- ✅ Users can view themselves
- ✅ Anyone can view servicemen (public)
- ❌ Clients are private (admin only)

### Response
```json
{
  "id": 1,
  "username": "john_electrician",
  "email": "john@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": true
}
```

### Example Usage
```bash
# Get user with ID 5
GET /api/users/5/
Authorization: Bearer YOUR_TOKEN
```

### Use Case: Display User Info
```javascript
// Get user details for display
async function getUserDetails(userId, token) {
  const response = await fetch(`/api/users/${userId}/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    if (response.status === 403) {
      return { error: "No permission to view this user" };
    }
    throw new Error('Failed to fetch user');
  }
  
  return await response.json();
}

// Usage
const user = await getUserDetails(5, adminToken);
console.log(`${user.username} (${user.user_type})`);
```

---

## 🎯 3. GET /users/clients/{client_id}/

**Get client profile by ID**

### Endpoint
```
GET /api/users/clients/{client_id}/
```

### Authentication
Required: Yes (Admin or self)

### Access Control
- ✅ Admins can view any client
- ✅ Clients can view their own profile
- ❌ Servicemen cannot view client profiles

### Response
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
  "updated_at": "2025-10-17T14:30:00Z"
}
```

### Example Usage
```bash
# Get client profile with ID 10
GET /api/users/clients/10/
Authorization: Bearer ADMIN_TOKEN
```

### Use Case: Service Request Client Info
```javascript
// Display client details in service request
async function getClientDetails(clientId, adminToken) {
  const response = await fetch(`/api/users/clients/${clientId}/`, {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch client details');
  }
  
  return await response.json();
}

// Usage in service request detail page
function ServiceRequestDetails({ request, adminToken }) {
  const [clientData, setClientData] = useState(null);
  
  useEffect(() => {
    getClientDetails(request.client_id, adminToken)
      .then(setClientData);
  }, [request.client_id]);
  
  return (
    <div>
      <h3>Client Information</h3>
      {clientData && (
        <div>
          <p>Name: {clientData.user.username}</p>
          <p>Email: {clientData.user.email}</p>
          <p>Phone: {clientData.phone_number}</p>
          <p>Address: {clientData.address}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 4. POST /notifications/send/

**Send notification to a user**

### Endpoint
```
POST /api/notifications/send/
```

### Authentication
Required: Yes (Admin only)

### Request Body
```json
{
  "user_id": 5,
  "title": "Service Request Assigned",
  "message": "You have been assigned to service request #123. Please review the details.",
  "notification_type": "SERVICE_ASSIGNED",
  "service_request_id": 123
}
```

### Required Fields
- `user_id` (integer) - ID of user to notify
- `title` (string) - Notification title
- `message` (string) - Notification message

### Optional Fields
- `notification_type` (string) - Type of notification. Options:
  - `SERVICE_ASSIGNED` (default)
  - `PAYMENT_RECEIVED`
  - `COST_ESTIMATE_READY`
  - `NEGOTIATION_UPDATE`
  - `JOB_COMPLETED`
  - `BACKUP_OPPORTUNITY`
- `service_request_id` (integer) - Related service request

### Response
```json
{
  "detail": "Notification sent successfully",
  "notification": {
    "id": 45,
    "user": 5,
    "notification_type": "SERVICE_ASSIGNED",
    "title": "Service Request Assigned",
    "message": "You have been assigned to service request #123...",
    "service_request": 123,
    "is_read": false,
    "created_at": "2025-10-17T15:30:00Z"
  },
  "email_queued": true,
  "recipient": {
    "id": 5,
    "username": "john_electrician",
    "email": "john@example.com",
    "user_type": "SERVICEMAN"
  }
}
```

### Example Usage
```bash
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "title": "New Service Assignment",
    "message": "You have been assigned to service request #123",
    "notification_type": "SERVICE_ASSIGNED",
    "service_request_id": 123
  }'
```

### Use Case: Notify Serviceman on Assignment
```javascript
// Notify serviceman when admin assigns them
async function notifyServicemanAssignment(serviceRequest, servicemanId, adminToken) {
  const response = await fetch('/api/notifications/send/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: servicemanId,
      title: 'New Service Request Assigned',
      message: `You have been assigned to service request #${serviceRequest.id}. ` +
               `Category: ${serviceRequest.category.name}. ` +
               `Client: ${serviceRequest.client.username}. ` +
               `Location: ${serviceRequest.client_address}. ` +
               `Please review and accept the assignment.`,
      notification_type: 'SERVICE_ASSIGNED',
      service_request_id: serviceRequest.id
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to send notification');
  }
  
  const data = await response.json();
  console.log('Notification sent:', data.detail);
  
  return data;
}

// Usage: After admin assigns serviceman
function assignServiceman(requestId, servicemanId) {
  // 1. Update service request with serviceman
  updateServiceRequest(requestId, { serviceman_id: servicemanId })
    .then(request => {
      // 2. Send notification
      return notifyServicemanAssignment(request, servicemanId, adminToken);
    })
    .then(() => {
      alert('Serviceman assigned and notified!');
    });
}
```

### Notification Types & Use Cases

| Type | When to Use | Example Message |
|------|-------------|-----------------|
| `SERVICE_ASSIGNED` | Admin assigns serviceman | "You've been assigned to SR #123" |
| `PAYMENT_RECEIVED` | Client completes payment | "Payment of ₦50,000 received for SR #123" |
| `COST_ESTIMATE_READY` | Serviceman submits estimate | "Cost estimate ready for review" |
| `NEGOTIATION_UPDATE` | Price negotiation update | "Client has countered your offer" |
| `JOB_COMPLETED` | Serviceman marks job done | "Service request #123 completed" |
| `BACKUP_OPPORTUNITY` | Backup serviceman needed | "You're backup for SR #123" |

---

## 📊 Complete Admin Workflow Example

### Assigning a Service Request

```javascript
// Complete workflow: Assign serviceman and notify
async function completeServiceAssignment(requestId, servicemanId, backupId, adminToken) {
  try {
    // 1. Get serviceman details
    const serviceman = await fetch(`/api/users/servicemen/${servicemanId}/`, {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    }).then(r => r.json());
    
    // 2. Update service request
    const request = await fetch(`/api/service-requests/${requestId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        serviceman_id: servicemanId,
        backup_serviceman_id: backupId,
        status: 'ASSIGNED_TO_SERVICEMAN'
      })
    }).then(r => r.json());
    
    // 3. Notify primary serviceman
    await fetch('/api/notifications/send/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: servicemanId,
        title: 'New Service Request Assigned',
        message: `You have been assigned to service request #${requestId}. ` +
                 `Client: ${request.client.username}. ` +
                 `Category: ${request.category.name}. ` +
                 `Please accept and schedule inspection.`,
        notification_type: 'SERVICE_ASSIGNED',
        service_request_id: requestId
      })
    });
    
    // 4. Notify backup serviceman
    if (backupId) {
      await fetch('/api/notifications/send/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: backupId,
          title: 'Backup Service Opportunity',
          message: `You have been assigned as backup for service request #${requestId}. ` +
                   `You'll be notified if the primary serviceman declines.`,
          notification_type: 'BACKUP_OPPORTUNITY',
          service_request_id: requestId
        })
      });
    }
    
    return { success: true, request };
    
  } catch (error) {
    console.error('Assignment failed:', error);
    return { success: false, error: error.message };
  }
}
```

---

## 📋 Quick Reference Table

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/users/servicemen/` | GET | Yes | List all servicemen |
| `/api/users/{id}/` | GET | Yes | Get any user by ID |
| `/api/users/clients/{id}/` | GET | Admin | Get client profile |
| `/api/notifications/send/` | POST | Admin | Send notification |

---

## 🔒 Authentication

All endpoints require JWT authentication:

```javascript
// Get token
const loginResponse = await fetch('/api/users/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});

const { access } = await loginResponse.json();

// Use token in requests
const headers = {
  'Authorization': `Bearer ${access}`,
  'Content-Type': 'application/json'
};
```

---

## 🧪 Testing

### Test All Endpoints

```bash
# 1. Get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.access')

# 2. List servicemen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users/servicemen/

# 3. Get user by ID
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users/5/

# 4. Get client profile
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users/clients/10/

# 5. Send notification
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "title": "Test Notification",
    "message": "This is a test"
  }'
```

---

## 📞 Support

For issues or questions:
- API Docs: `http://localhost:8000/api/docs/`
- Email: support@servicemanplatform.com

---

**Status**: ✅ ALL ENDPOINTS READY  
**Version**: 1.0.0  
**Last Updated**: October 2025


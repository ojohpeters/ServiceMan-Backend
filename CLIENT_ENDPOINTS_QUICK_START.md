# ⚡ Quick Start - Client Requested Endpoints

## ✅ All 4 Endpoints Ready!

---

## 1. List All Servicemen (For Admin Assignment)

```bash
GET /api/users/servicemen/
```

**Use:** Admin selects serviceman to assign to job

**Response includes:**
- Availability status (available/busy)
- Active jobs count  
- Skills, ratings, experience
- Statistics

**Filters:**
```bash
# Only available
?is_available=true

# By category
?category=1

# Min rating
?min_rating=4.5

# Search name
?search=john
```

**JavaScript:**
```javascript
const data = await fetch('/api/users/servicemen/?is_available=true', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// data.statistics.available = count of available servicemen
// data.results = array of servicemen
```

---

## 2. Get User by ID

```bash
GET /api/users/{user_id}/
```

**Use:** Display client/serviceman info

**JavaScript:**
```javascript
const user = await fetch('/api/users/5/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// user.username, user.email, user.user_type
```

---

## 3. Get Client Profile

```bash
GET /api/users/clients/{client_id}/
```

**Use:** Show client details in service requests

**JavaScript:**
```javascript
const client = await fetch('/api/users/clients/10/', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
}).then(r => r.json());

// client.phone_number, client.address
```

---

## 4. Send Notification

```bash
POST /api/notifications/send/
```

**Use:** Notify serviceman when assigned

**JavaScript:**
```javascript
await fetch('/api/notifications/send/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: 5,
    title: 'Service Request Assigned',
    message: 'You have been assigned to SR #123',
    notification_type: 'SERVICE_ASSIGNED',
    service_request_id: 123
  })
});
```

---

## 🎯 Complete Admin Assignment Flow

```javascript
// Step 1: Get available servicemen for category
const servicemenData = await fetch(
  `/api/users/servicemen/?category=${categoryId}&is_available=true`,
  { headers: { 'Authorization': `Bearer ${adminToken}` }}
).then(r => r.json());

// Step 2: Select serviceman (or show in UI)
const servicemanId = servicemenData.results[0].user;

// Step 3: Assign to request
await fetch(`/api/service-requests/${requestId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    serviceman_id: servicemanId,
    status: 'ASSIGNED_TO_SERVICEMAN'
  })
});

// Step 4: Notify serviceman
await fetch('/api/notifications/send/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: servicemanId,
    title: 'New Service Assignment',
    message: `You have been assigned to service request #${requestId}`,
    notification_type: 'SERVICE_ASSIGNED',
    service_request_id: requestId
  })
});

alert('Serviceman assigned and notified!');
```

---

## 📚 Full Documentation

**Detailed Guide**: `FRONTEND_API_CONSUMPTION_GUIDE.md`  
**Complete Reference**: `CLIENT_API_ENDPOINTS_GUIDE.md`  
**API Docs**: http://localhost:8000/api/docs/

---

**Status**: ✅ Ready to Use  
**All 4 Endpoints**: Implemented  
**Documentation**: Complete


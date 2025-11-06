# 🕐 Timezone & Client Details Update

## Version 2.2 | Last Updated: November 6, 2025

---

## 🎯 Two Critical Updates

### 1. ⏰ Notification Timestamps - Timezone Explanation

#### The Issue
Frontend is seeing "6h ago" when they expect "seconds ago" for recent notifications.

#### Root Cause
**Backend uses UTC timezone** (Universal Time Coordinated), which is the international standard for APIs.

```python
# Django Default Settings
TIME_ZONE = 'UTC'
USE_TZ = True
```

#### What Backend Returns

```json
{
  "id": 123,
  "title": "New Service Request",
  "message": "Client John Doe has booked a service",
  "created_at": "2025-11-06T14:30:00Z",  // ⚠️ This is UTC time
  "is_read": false
}
```

#### ✅ Frontend Solution

The frontend **MUST convert UTC timestamps to local time** before displaying.

##### Option 1: Using `date-fns` (Recommended)

```bash
npm install date-fns
```

```javascript
import { formatDistanceToNow } from 'date-fns';

function NotificationItem({ notification }) {
  const timeAgo = formatDistanceToNow(new Date(notification.created_at), {
    addSuffix: true, // Adds "ago"
  });

  return (
    <div>
      <p>{notification.message}</p>
      <small>{timeAgo}</small> {/* Will show "3 minutes ago" */}
    </div>
  );
}
```

##### Option 2: Using `moment.js`

```bash
npm install moment
```

```javascript
import moment from 'moment';

function NotificationItem({ notification }) {
  const timeAgo = moment(notification.created_at).fromNow();

  return (
    <div>
      <p>{notification.message}</p>
      <small>{timeAgo}</small> {/* Will show "3 minutes ago" */}
    </div>
  );
}
```

##### Option 3: Native JavaScript (No Dependencies)

```javascript
function timeAgo(dateString) {
  const now = new Date();
  const date = new Date(dateString);
  const seconds = Math.floor((now - date) / 1000);

  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };

  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
    }
  }
  return 'just now';
}

// Usage
function NotificationItem({ notification }) {
  return (
    <div>
      <p>{notification.message}</p>
      <small>{timeAgo(notification.created_at)}</small>
    </div>
  );
}
```

#### 🎯 Real Example

```javascript
// Backend returns (UTC):
"created_at": "2025-11-06T14:30:00Z"

// If user is in Nigeria (UTC+1):
// Browser automatically converts to: 2025-11-06T15:30:00

// date-fns will show:
formatDistanceToNow(new Date("2025-11-06T14:30:00Z"))
// Output: "3 minutes ago" (correct!)

// WITHOUT conversion (treating as local time):
// Would show "6h ago" (WRONG!)
```

#### ⚠️ Why Backend Uses UTC

1. **Global Standard**: Works for users in any timezone
2. **Consistency**: All times stored in same timezone
3. **No Daylight Saving Issues**: UTC never changes
4. **Best Practice**: All major APIs (Google, Facebook, Twitter) use UTC

#### 🚀 Complete React Component Example

```javascript
import React from 'react';
import { formatDistanceToNow } from 'date-fns';

function NotificationList() {
  const [notifications, setNotifications] = React.useState([]);

  React.useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    const response = await fetch('/api/notifications/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    const data = await response.json();
    setNotifications(data.results || data);
  };

  return (
    <div className="notification-list">
      {notifications.map(notification => (
        <div key={notification.id} className="notification-item">
          <h4>{notification.title}</h4>
          <p>{notification.message}</p>
          <small className="text-muted">
            {formatDistanceToNow(new Date(notification.created_at), {
              addSuffix: true
            })}
          </small>
        </div>
      ))}
    </div>
  );
}
```

---

### 2. 📞 Client Phone Number Now Included

#### The Issue
Service request endpoint was returning client details **without phone number**.

```json
// ❌ Before (incomplete)
"client": {
  "id": 5,
  "username": "johndoe",
  "email": "john@example.com",
  "user_type": "CLIENT",
  "is_email_verified": true
}
```

#### ✅ Fixed Response

```json
// ✅ After (complete)
"client": {
  "id": 5,
  "username": "johndoe",
  "email": "john@example.com",
  "user_type": "CLIENT",
  "is_email_verified": true,
  "phone_number": "+2348012345678"  // ✅ NEW!
}
```

#### What Changed

**Backend Updates:**

1. **Serializer Enhancement**:
   - `UserSerializer` now includes `phone_number` field
   - `UserBasicSerializer` now includes `phone_number` field
   - Both fetch phone number from `ClientProfile` model

2. **Query Optimization**:
   - Added `client__client_profile` to `prefetch_related()`
   - No extra database queries
   - Phone number available instantly

#### 📋 Affected Endpoints

All endpoints returning `client` object now include phone number:

1. **GET** `/api/services/service-requests/` - List view
2. **GET** `/api/services/service-requests/{id}/` - Detail view
3. **GET** `/api/notifications/` - Notifications (if client is referenced)

#### Frontend Usage

```javascript
// Fetch service request
const response = await fetch('/api/services/service-requests/9/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const serviceRequest = await response.json();

// ✅ Access client phone number
console.log(serviceRequest.client.phone_number);
// Output: "+2348012345678"

// Display in UI
<div className="client-contact">
  <h3>Client Contact</h3>
  <p>Name: {serviceRequest.client.username}</p>
  <p>Email: {serviceRequest.client.email}</p>
  <p>Phone: {serviceRequest.client.phone_number || 'Not provided'}</p>
</div>
```

#### 🎯 Complete Example: Service Request Details

```javascript
import React from 'react';
import { formatDistanceToNow } from 'date-fns';

function ServiceRequestDetails({ requestId }) {
  const [request, setRequest] = React.useState(null);

  React.useEffect(() => {
    fetchRequest();
  }, [requestId]);

  const fetchRequest = async () => {
    const response = await fetch(`/api/services/service-requests/${requestId}/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    const data = await response.json();
    setRequest(data);
  };

  if (!request) return <div>Loading...</div>;

  return (
    <div className="service-request-details">
      <h2>Service Request #{request.id}</h2>
      
      {/* Client Details with Phone Number */}
      <div className="client-section">
        <h3>Client Information</h3>
        <p><strong>Name:</strong> {request.client.username}</p>
        <p><strong>Email:</strong> {request.client.email}</p>
        <p><strong>Phone:</strong> {request.client.phone_number || 'Not provided'}</p>
      </div>

      {/* Service Details */}
      <div className="service-section">
        <h3>Service Details</h3>
        <p><strong>Category:</strong> {request.category.name}</p>
        <p><strong>Status:</strong> {request.status}</p>
        <p><strong>Description:</strong> {request.service_description}</p>
        <p><strong>Address:</strong> {request.client_address}</p>
      </div>

      {/* Timestamps with Correct Timezone Handling */}
      <div className="timestamps">
        <p>
          <strong>Booking Date:</strong>{' '}
          {new Date(request.booking_date).toLocaleString()}
        </p>
        <p>
          <strong>Created:</strong>{' '}
          {formatDistanceToNow(new Date(request.created_at), {
            addSuffix: true
          })}
        </p>
      </div>

      {/* Serviceman Details (if assigned) */}
      {request.serviceman && (
        <div className="serviceman-section">
          <h3>Assigned Serviceman</h3>
          <p><strong>Name:</strong> {request.serviceman.user.full_name}</p>
          <p><strong>Rating:</strong> ⭐ {request.serviceman.rating}</p>
          <p><strong>Skills:</strong> {request.serviceman.skills.map(s => s.name).join(', ')}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🚀 Deployment Status

✅ **Backend Updated** - Changes deployed to production  
✅ **Database Optimized** - Phone number queries are efficient  
✅ **No Breaking Changes** - `phone_number` is optional (returns `null` if not set)  

---

## 📊 Summary

| Feature | Status | Action Required |
|---------|--------|-----------------|
| UTC Timestamps | ✅ Standard | Frontend: Convert to local time |
| Phone Number | ✅ Added | Frontend: Update UI to display phone |
| Query Optimization | ✅ Done | No action needed |
| Backward Compatible | ✅ Yes | Existing code won't break |

---

## ⚠️ Important Notes

1. **Timezone Conversion**:
   - Always happens on the **frontend**
   - Backend will always return UTC
   - Use `date-fns` or `moment.js` for easy conversion

2. **Phone Number**:
   - Returns `null` if client hasn't provided phone number
   - Always check before displaying: `client.phone_number || 'Not provided'`
   - Only available for `CLIENT` user type

3. **Performance**:
   - No extra database queries
   - Phone number is prefetched with service request
   - Timestamps are simple ISO strings

---

## 🔧 Testing

### Test Timezone Conversion

```javascript
// Test with current time
const utcTime = "2025-11-06T14:30:00Z";
console.log('UTC:', utcTime);
console.log('Local:', new Date(utcTime).toLocaleString());
console.log('Relative:', formatDistanceToNow(new Date(utcTime)));
```

### Test Phone Number Display

```javascript
// Test with mock data
const mockClient = {
  id: 1,
  username: "test",
  email: "test@example.com",
  phone_number: "+2348012345678"
};

console.log('Phone:', mockClient.phone_number || 'Not provided');
// Output: "Phone: +2348012345678"

const mockClientNoPhone = { ...mockClient, phone_number: null };
console.log('Phone:', mockClientNoPhone.phone_number || 'Not provided');
// Output: "Phone: Not provided"
```

---

## 📞 Support

If you encounter any issues:

1. **Timezone Issues**: Verify `date-fns` is installed and imported correctly
2. **Missing Phone Number**: Check if client profile has phone number set
3. **Performance Issues**: All queries are optimized, should be fast

---

**Backend Version**: 2.2  
**Effective Date**: November 6, 2025  
**Breaking Changes**: None  
**Migration Required**: No  


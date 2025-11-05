# 👥 Serviceman Selection & Assignment System - Complete Guide

**Last Updated:** November 5, 2025  
**Version:** 1.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [The Three Types of Servicemen](#the-three-types-of-servicemen)
3. [Client Selection Flow](#client-selection-flow)
4. [Admin Assignment Flow](#admin-assignment-flow)
5. [Notification System](#notification-system)
6. [API Endpoints](#api-endpoints)
7. [Frontend Implementation](#frontend-implementation)
8. [Use Cases & Scenarios](#use-cases--scenarios)
9. [Best Practices](#best-practices)

---

## 🎯 Overview

The ServiceMan platform uses a **three-tier serviceman system** to ensure quality service delivery and availability:

1. **Preferred Serviceman** - Client's choice (optional)
2. **Primary Serviceman** - Admin-assigned main worker
3. **Backup Serviceman** - Admin-assigned fallback option

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. CLIENT BOOKS SERVICE                                     │
│     ├─ Selects category                                      │
│     ├─ Optionally selects preferred serviceman               │
│     └─ Pays booking fee                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. ADMIN REVIEWS REQUEST                                    │
│     ├─ Sees client's preferred serviceman (if any)           │
│     ├─ Can assign preferred serviceman or choose different   │
│     ├─ Assigns primary serviceman (required)                 │
│     └─ Assigns backup serviceman (recommended)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. NOTIFICATIONS SENT                                       │
│     ├─ Primary serviceman: "New Job Assignment"              │
│     ├─ Backup serviceman: "Backup Assignment"                │
│     └─ Client: "Serviceman Assigned"                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. SERVICE DELIVERY                                         │
│     ├─ Primary serviceman contacts client                    │
│     ├─ Backup serviceman is on standby                       │
│     └─ If primary unavailable → backup takes over            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔢 The Three Types of Servicemen

### 1️⃣ Preferred Serviceman (Optional)

**What:** The serviceman the client **wants** to work with  
**Set By:** Client during booking  
**Purpose:** Give clients choice and control  
**Required:** No (optional field)

**Characteristics:**
- ✅ Client's personal choice (maybe worked with them before)
- ✅ Shows in admin dashboard as recommendation
- ⚠️ Admin can override (not guaranteed assignment)
- ⚠️ Does not receive notifications automatically
- ⚠️ Only gets assigned if admin confirms

**When Client Might Choose:**
- Previous positive experience with the serviceman
- Recommendation from friend/family
- Specific skills or expertise needed
- Trust and familiarity

---

### 2️⃣ Primary Serviceman (Required)

**What:** The serviceman **officially assigned** to the job  
**Set By:** Admin  
**Purpose:** Main person responsible for completing the service  
**Required:** Yes

**Characteristics:**
- ✅ Assigned by admin after reviewing request
- ✅ Receives "New Job Assignment" notification with full details
- ✅ Responsible for contacting client
- ✅ Must provide cost estimate
- ✅ Must complete the job
- ✅ Gets client contact information

**Notification Includes:**
- Full job details (category, date, address, description)
- Client contact information (name, phone)
- Next steps (contact client for site visit)
- Admin notes (if any)

---

### 3️⃣ Backup Serviceman (Recommended)

**What:** The **fallback option** if primary serviceman unavailable  
**Set By:** Admin  
**Purpose:** Ensure service continuity and availability  
**Required:** No (but highly recommended)

**Characteristics:**
- ✅ Assigned by admin along with primary serviceman
- ✅ Receives "Backup Assignment" notification
- ✅ Can step in if primary serviceman:
  - Is unavailable
  - Declines the job
  - Has an emergency
  - Is already overbooked
- ⚠️ Not automatically visible to client (unless becomes primary)
- ⚠️ Less detailed notification (basic job info only)

**Notification Includes:**
- Request ID and category
- Booking date
- Status: "Backup serviceman"
- Instructions to be on standby

---

## 📱 Client Selection Flow

### Step 1: Browse Servicemen

**Endpoint:** `GET /api/users/servicemen/?category=<category_id>`

```javascript
// Client browses servicemen in their category
const response = await fetch('/api/users/servicemen/?category=1', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const { results: servicemen } = await response.json();

// Display servicemen with:
// - Name, rating, total jobs completed
// - Years of experience
// - Skills
// - Availability status
```

---

### Step 2: (Optional) Select Preferred Serviceman

```jsx
// React Component Example
function ServicemanSelectionCard({ serviceman, onSelect, isSelected }) {
  return (
    <div className={`serviceman-card ${isSelected ? 'selected' : ''}`}>
      <img src={serviceman.avatar} alt={serviceman.user.full_name} />
      
      <div className="serviceman-info">
        <h3>{serviceman.user.full_name}</h3>
        <div className="rating">
          ⭐ {serviceman.rating} ({serviceman.total_jobs_completed} jobs)
        </div>
        <div className="experience">
          {serviceman.years_of_experience} years experience
        </div>
        <div className="skills">
          {serviceman.skills.map(skill => (
            <span key={skill.id} className="skill-badge">
              {skill.name}
            </span>
          ))}
        </div>
        <div className={`availability ${serviceman.is_available ? 'available' : 'busy'}`}>
          {serviceman.is_available ? '✓ Available' : '⚠ Currently Busy'}
        </div>
      </div>
      
      <button 
        onClick={() => onSelect(serviceman.id)}
        className={isSelected ? 'btn-selected' : 'btn-select'}
      >
        {isSelected ? '✓ Selected as Preferred' : 'Select This Serviceman'}
      </button>
    </div>
  );
}
```

---

### Step 3: Create Service Request with Preference

**Endpoint:** `POST /api/services/service-requests/`

```javascript
// Create service request with optional preferred serviceman
const createServiceRequest = async (requestData) => {
  const response = await fetch('/api/services/service-requests/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      payment_reference: requestData.paymentReference,  // Required
      category_id: requestData.categoryId,              // Required
      booking_date: requestData.bookingDate,            // Required
      client_address: requestData.address,              // Required
      service_description: requestData.description,     // Required
      is_emergency: requestData.isEmergency,            // Optional
      preferred_serviceman_id: requestData.preferredServicemanId  // ✨ NEW: Optional
    })
  });

  if (response.ok) {
    const serviceRequest = await response.json();
    console.log('✅ Service request created!');
    console.log('Preferred serviceman:', serviceRequest.preferred_serviceman);
    return serviceRequest;
  }
};

// Example usage
await createServiceRequest({
  paymentReference: 'PAY_xyz123',
  categoryId: 1,
  bookingDate: '2025-11-15',
  address: '123 Main St, Lagos',
  description: 'Fix leaking pipe in kitchen',
  isEmergency: false,
  preferredServicemanId: 42  // Optional: Client's preferred serviceman
});
```

**Response (201 Created):**
```json
{
  "id": 789,
  "client": {
    "id": 10,
    "username": "jane_doe",
    "email": "jane@example.com",
    "full_name": "Jane Doe",
    "user_type": "CLIENT"
  },
  "preferred_serviceman": {
    "id": 42,
    "username": "john_plumber",
    "email": "john@example.com",
    "full_name": "John Plumber",
    "user_type": "SERVICEMAN"
  },
  "serviceman": null,
  "backup_serviceman": null,
  "category": {
    "id": 1,
    "name": "Plumbing",
    "icon_url": "🔧"
  },
  "booking_date": "2025-11-15",
  "status": "PENDING_ADMIN_ASSIGNMENT",
  "client_address": "123 Main St, Lagos",
  "service_description": "Fix leaking pipe in kitchen",
  "is_emergency": false,
  "created_at": "2025-11-05T10:30:00Z"
}
```

---

## 👨‍💼 Admin Assignment Flow

### Step 1: View Pending Requests

**Endpoint:** `GET /api/services/service-requests/?status=PENDING_ADMIN_ASSIGNMENT`

```javascript
// Admin views pending requests
const getPendingRequests = async () => {
  const response = await fetch(
    '/api/services/service-requests/?status=PENDING_ADMIN_ASSIGNMENT',
    {
      headers: {
        'Authorization': `Bearer ${adminAccessToken}`
      }
    }
  );

  const { results: requests } = await response.json();
  
  // Each request shows:
  // - Client info
  // - Category and description
  // - Preferred serviceman (if client selected one) ✨
  // - Booking date
  // - Emergency status
  
  return requests;
};
```

---

### Step 2: Review Client's Preference

```jsx
// React Component: Admin Request Card
function AdminRequestCard({ request }) {
  return (
    <div className="admin-request-card">
      <div className="request-header">
        <h3>Request #{request.id}</h3>
        {request.is_emergency && (
          <span className="badge-emergency">🚨 EMERGENCY</span>
        )}
      </div>

      <div className="client-info">
        <h4>Client: {request.client.full_name}</h4>
        <p>Phone: {request.client.phone_number}</p>
        <p>Address: {request.client_address}</p>
      </div>

      <div className="service-details">
        <p><strong>Category:</strong> {request.category.name}</p>
        <p><strong>Date:</strong> {request.booking_date}</p>
        <p><strong>Description:</strong> {request.service_description}</p>
      </div>

      {/* ✨ Show client's preference if provided */}
      {request.preferred_serviceman && (
        <div className="client-preference">
          <h4>💡 Client's Preferred Serviceman:</h4>
          <div className="preferred-serviceman-info">
            <img src={request.preferred_serviceman.avatar} alt=""/>
            <div>
              <strong>{request.preferred_serviceman.user.full_name}</strong>
              <p>⭐ Rating: {request.preferred_serviceman.rating}</p>
              <p>📊 {request.preferred_serviceman.total_jobs_completed} jobs completed</p>
              <p className={request.preferred_serviceman.is_available ? 'available' : 'busy'}>
                {request.preferred_serviceman.is_available ? '✓ Available Now' : '⚠ Currently Busy'}
              </p>
            </div>
          </div>
          <button 
            className="btn-use-preference"
            onClick={() => assignServiceman(request.id, request.preferred_serviceman.id)}
          >
            ✓ Assign Client's Preferred Serviceman
          </button>
        </div>
      )}

      <div className="assignment-actions">
        <button onClick={() => openAssignmentModal(request.id)}>
          Assign Servicemen
        </button>
      </div>
    </div>
  );
}
```

---

### Step 3: Assign Primary & Backup Servicemen

**Endpoint:** `POST /api/services/service-requests/<id>/assign/`

```javascript
// Assign servicemen to a request
const assignServicemen = async (requestId, primaryId, backupId, notes = '') => {
  const response = await fetch(`/api/services/service-requests/${requestId}/assign/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminAccessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      serviceman_id: primaryId,           // Required: Primary serviceman
      backup_serviceman_id: backupId,     // Optional: Backup serviceman
      notes: notes                         // Optional: Admin notes for serviceman
    })
  });

  if (response.ok) {
    console.log('✅ Servicemen assigned successfully!');
    console.log('📧 Notifications sent to both servicemen and client');
    return await response.json();
  }
};

// Example 1: Assign client's preferred serviceman + backup
await assignServicemen(
  789,  // Request ID
  42,   // Primary: Client's preferred serviceman
  55,   // Backup: Another qualified serviceman
  'Client requested this serviceman specifically. Please prioritize.'
);

// Example 2: Assign different serviceman (override client preference)
await assignServicemen(
  789,  // Request ID
  38,   // Primary: Different serviceman (preferred one was busy)
  42,   // Backup: Client's preferred serviceman as backup
  'Client\'s preferred serviceman was unavailable. Assigned John instead. Client\'s preference added as backup.'
);
```

**Response (200 OK):**
```json
{
  "detail": "Servicemen assigned successfully",
  "service_request": {
    "id": 789,
    "preferred_serviceman": {
      "id": 42,
      "username": "john_plumber",
      "full_name": "John Plumber"
    },
    "serviceman": {
      "id": 42,
      "username": "john_plumber",
      "full_name": "John Plumber"
    },
    "backup_serviceman": {
      "id": 55,
      "username": "mike_plumber",
      "full_name": "Mike Smith"
    },
    "status": "PENDING_ESTIMATION"
  },
  "notifications_sent": {
    "primary_serviceman": true,
    "backup_serviceman": true,
    "client": true
  }
}
```

---

## 🔔 Notification System

### Primary Serviceman Notification

**When:** Admin assigns primary serviceman  
**Recipient:** Primary serviceman  
**Type:** `JOB_ASSIGNED`

**Notification Content:**
```
Title: New Job Assignment - Request #789

Message:
You have been assigned to a new service request.

📋 Job Details:
• Category: Plumbing
• Booking Date: 2025-11-15
• Address: 123 Main St, Lagos
• Description: Fix leaking pipe in kitchen

👤 Client Contact:
• Name: Jane Doe
• Phone: +234 123 456 7890

📝 Next Step: Please contact the client to schedule a site visit and provide a cost estimate.

Admin Notes: Client requested you specifically. Please prioritize.
```

---

### Backup Serviceman Notification

**When:** Admin assigns backup serviceman  
**Recipient:** Backup serviceman  
**Type:** `SERVICE_ASSIGNED`

**Notification Content:**
```
Title: Service Request Backup Assignment

Message:
You have been assigned as backup serviceman for request #789.
Category: Plumbing.
Date: 2025-11-15.

You may be contacted if the primary serviceman becomes unavailable.
```

---

### Client Notification

**When:** Admin assigns serviceman  
**Recipient:** Client  
**Type:** `STATUS_UPDATE`

**Notification Content:**
```
Title: Serviceman Assigned - Request #789

Message:
Good news! A serviceman has been assigned to your service request.

The serviceman will contact you shortly to schedule a site visit and discuss your requirements.

Please ensure you are available at the provided address.
```

---

## 📡 API Endpoints

### 1. List Available Servicemen (For Client Selection)

```http
GET /api/users/servicemen/?category=<category_id>
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `category` - Filter by category ID
- `is_available` - Filter by availability (true/false)
- `min_rating` - Filter by minimum rating
- `search` - Search by name or username

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 42,
      "user": {
        "id": 42,
        "username": "john_plumber",
        "full_name": "John Plumber",
        "email": "john@example.com"
      },
      "category": {
        "id": 1,
        "name": "Plumbing",
        "icon": "🔧"
      },
      "skills": [
        {"id": 1, "name": "Pipe Repair"},
        {"id": 2, "name": "Leak Detection"}
      ],
      "rating": "4.70",
      "total_jobs_completed": 85,
      "years_of_experience": 12,
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

### 2. Create Service Request with Preferred Serviceman

```http
POST /api/services/service-requests/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "payment_reference": "PAY_xyz123",
  "category_id": 1,
  "booking_date": "2025-11-15",
  "client_address": "123 Main St, Lagos",
  "service_description": "Fix leaking pipe in kitchen",
  "is_emergency": false,
  "preferred_serviceman_id": 42
}
```

**Fields:**
- `payment_reference` (string, required) - Paystack payment reference
- `category_id` (int, required) - Service category ID
- `booking_date` (date, required) - Preferred booking date (YYYY-MM-DD)
- `client_address` (string, required) - Service location address
- `service_description` (string, required) - Description of service needed
- `is_emergency` (boolean, optional) - Emergency booking flag
- `preferred_serviceman_id` (int, optional) - ✨ **NEW:** Client's preferred serviceman ID

---

### 3. Admin: View Service Request (Shows Preference)

```http
GET /api/services/service-requests/<id>/
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "id": 789,
  "client": {
    "id": 10,
    "username": "jane_doe",
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone_number": "+234 123 456 7890"
  },
  "preferred_serviceman": {
    "id": 42,
    "user": {
      "id": 42,
      "username": "john_plumber",
      "full_name": "John Plumber"
    },
    "rating": "4.70",
    "total_jobs_completed": 85,
    "is_available": true
  },
  "serviceman": null,
  "backup_serviceman": null,
  "status": "PENDING_ADMIN_ASSIGNMENT",
  "category": {
    "id": 1,
    "name": "Plumbing"
  },
  "booking_date": "2025-11-15",
  "client_address": "123 Main St, Lagos",
  "service_description": "Fix leaking pipe in kitchen",
  "is_emergency": false
}
```

---

### 4. Admin: Assign Servicemen

```http
POST /api/services/service-requests/<id>/assign/
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "serviceman_id": 42,
  "backup_serviceman_id": 55,
  "notes": "Client requested this serviceman. Please prioritize."
}
```

**Validation Rules:**
- ✅ Primary serviceman must be approved
- ✅ Backup serviceman must be approved
- ✅ Primary and backup cannot be the same person
- ✅ Both must have user_type = 'SERVICEMAN'

---

## 💻 Frontend Implementation

### Complete Booking Flow with Serviceman Selection

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';

function ServiceBookingPage() {
  const { accessToken } = useAuth();
  const [step, setStep] = useState(1);
  const [category, setCategory] = useState(null);
  const [servicemen, setServicemen] = useState([]);
  const [selectedServiceman, setSelectedServiceman] = useState(null);
  const [bookingData, setBookingData] = useState({
    date: '',
    address: '',
    description: '',
    isEmergency: false
  });

  // Step 1: Select category (not shown here)

  // Step 2: Browse and select serviceman (optional)
  useEffect(() => {
    if (category) {
      fetchServicemen(category.id);
    }
  }, [category]);

  const fetchServicemen = async (categoryId) => {
    const response = await fetch(
      `/api/users/servicemen/?category=${categoryId}`,
      {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }
    );
    const data = await response.json();
    setServicemen(data.results || []);
  };

  // Step 3: Fill booking details
  const handleBookingSubmit = async () => {
    // Step 3a: Initialize payment
    const paymentResponse = await fetch('/api/payments/initialize-booking-fee/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: bookingData.isEmergency ? 5000 : 2000,
        is_emergency: bookingData.isEmergency,
        callback_url: `${window.location.origin}/verify-payment`
      })
    });

    const paymentData = await paymentResponse.json();

    // Step 3b: Redirect to Paystack
    window.location.href = paymentData.authorization_url;
  };

  // Step 4: After payment (on callback page)
  const createServiceRequest = async (paymentReference) => {
    const response = await fetch('/api/services/service-requests/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_reference: paymentReference,
        category_id: category.id,
        booking_date: bookingData.date,
        client_address: bookingData.address,
        service_description: bookingData.description,
        is_emergency: bookingData.isEmergency,
        preferred_serviceman_id: selectedServiceman?.id  // Optional
      })
    });

    if (response.ok) {
      const serviceRequest = await response.json();
      alert('✅ Service request created successfully!');
      
      if (selectedServiceman) {
        alert(`Your preferred serviceman (${selectedServiceman.user.full_name}) has been noted. The admin will review and assign servicemen shortly.`);
      }

      // Redirect to requests page
      window.location.href = '/my-requests';
    }
  };

  return (
    <div className="booking-page">
      {step === 2 && (
        <div className="serviceman-selection">
          <h2>Choose Your Preferred Serviceman (Optional)</h2>
          <p className="info-text">
            Select a serviceman you'd like to work with. The admin will review
            your preference when assigning servicemen to your request.
          </p>

          <div className="serviceman-grid">
            {servicemen.map(serviceman => (
              <ServicemanCard
                key={serviceman.id}
                serviceman={serviceman}
                isSelected={selectedServiceman?.id === serviceman.id}
                onSelect={() => setSelectedServiceman(serviceman)}
              />
            ))}
          </div>

          <div className="selection-actions">
            {selectedServiceman && (
              <div className="selected-info">
                ✓ You selected: <strong>{selectedServiceman.user.full_name}</strong>
                <button onClick={() => setSelectedServiceman(null)}>
                  Clear Selection
                </button>
              </div>
            )}

            <button onClick={() => setStep(3)}>
              {selectedServiceman ? 'Continue with Selection' : 'Skip - Let Admin Choose'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Booking details form */}
    </div>
  );
}
```

---

### Admin Assignment Interface

```jsx
function AdminAssignmentModal({ request, onClose }) {
  const [primaryServiceman, setPrimaryServiceman] = useState(null);
  const [backupServiceman, setBackupServiceman] = useState(null);
  const [notes, setNotes] = useState('');
  const [servicemen, setServicemen] = useState([]);

  useEffect(() => {
    // Fetch available servicemen in request category
    fetchServicemen();
  }, []);

  const fetchServicemen = async () => {
    const response = await fetch(
      `/api/users/servicemen/?category=${request.category.id}&is_available=true`
    );
    const data = await response.json();
    setServicemen(data.results || []);
  };

  const handleAssign = async () => {
    if (!primaryServiceman) {
      alert('Please select a primary serviceman');
      return;
    }

    if (primaryServiceman.id === backupServiceman?.id) {
      alert('Primary and backup servicemen cannot be the same');
      return;
    }

    const response = await fetch(
      `/api/services/service-requests/${request.id}/assign/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          serviceman_id: primaryServiceman.id,
          backup_serviceman_id: backupServiceman?.id,
          notes: notes
        })
      }
    );

    if (response.ok) {
      alert('✅ Servicemen assigned successfully!');
      onClose();
    }
  };

  return (
    <div className="assignment-modal">
      <h2>Assign Servicemen - Request #{request.id}</h2>

      {/* Show client's preference */}
      {request.preferred_serviceman && (
        <div className="client-preference-section">
          <h3>💡 Client's Preferred Serviceman:</h3>
          <div className="preferred-serviceman-card">
            <strong>{request.preferred_serviceman.user.full_name}</strong>
            <p>⭐ {request.preferred_serviceman.rating} rating</p>
            <p>📊 {request.preferred_serviceman.total_jobs_completed} jobs</p>
            <p className={request.preferred_serviceman.is_available ? 'available' : 'busy'}>
              {request.preferred_serviceman.is_available ? '✓ Available' : '⚠ Busy'}
            </p>
            <button onClick={() => setPrimaryServiceman(request.preferred_serviceman)}>
              ✓ Use Client's Preference
            </button>
          </div>
        </div>
      )}

      {/* Primary serviceman selection */}
      <div className="serviceman-selection-section">
        <h3>Primary Serviceman (Required)</h3>
        <select
          value={primaryServiceman?.id || ''}
          onChange={(e) => {
            const serviceman = servicemen.find(s => s.id === parseInt(e.target.value));
            setPrimaryServiceman(serviceman);
          }}
        >
          <option value="">-- Select Primary Serviceman --</option>
          {servicemen.map(serviceman => (
            <option key={serviceman.id} value={serviceman.id}>
              {serviceman.user.full_name} - ⭐ {serviceman.rating} ({serviceman.total_jobs_completed} jobs)
              {serviceman.is_available ? ' ✓ Available' : ' ⚠ Busy'}
            </option>
          ))}
        </select>
      </div>

      {/* Backup serviceman selection */}
      <div className="serviceman-selection-section">
        <h3>Backup Serviceman (Recommended)</h3>
        <select
          value={backupServiceman?.id || ''}
          onChange={(e) => {
            const serviceman = servicemen.find(s => s.id === parseInt(e.target.value));
            setBackupServiceman(serviceman);
          }}
        >
          <option value="">-- Select Backup Serviceman --</option>
          {servicemen
            .filter(s => s.id !== primaryServiceman?.id)
            .map(serviceman => (
              <option key={serviceman.id} value={serviceman.id}>
                {serviceman.user.full_name} - ⭐ {serviceman.rating}
              </option>
            ))}
        </select>
      </div>

      {/* Admin notes */}
      <div className="notes-section">
        <h3>Notes for Serviceman (Optional)</h3>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add any special instructions or notes..."
          rows={4}
        />
      </div>

      {/* Actions */}
      <div className="modal-actions">
        <button onClick={onClose}>Cancel</button>
        <button onClick={handleAssign} className="btn-primary">
          Assign Servicemen & Send Notifications
        </button>
      </div>
    </div>
  );
}
```

---

## 🎭 Use Cases & Scenarios

### Scenario 1: Client Trusts Specific Serviceman

**Situation:** Jane had a great experience with John the plumber last month.

**Flow:**
1. Jane books a new plumbing service
2. Jane selects John as her preferred serviceman
3. Admin reviews and sees Jane's preference
4. Admin assigns John as primary serviceman
5. John receives notification and contacts Jane
6. **Result:** Client satisfaction ⬆️ Trust ⬆️

---

### Scenario 2: Preferred Serviceman is Unavailable

**Situation:** Client requests John, but John is fully booked.

**Flow:**
1. Client selects John as preferred serviceman
2. Admin sees John is busy (4 active jobs)
3. Admin assigns Mike as primary serviceman (available, similar rating)
4. Admin assigns John as backup serviceman
5. Mike receives primary assignment notification
6. John receives backup notification ("may be contacted if primary unavailable")
7. Client receives notification: "Serviceman assigned"
8. **Result:** Service continuity maintained ✅

---

### Scenario 3: No Preference Given

**Situation:** New client doesn't know any servicemen.

**Flow:**
1. Client skips serviceman selection
2. `preferred_serviceman_id` is null
3. Admin reviews request and assigns best available serviceman
4. Admin considers: rating, availability, workload, location
5. Admin assigns primary + backup
6. **Result:** Admin has full flexibility 👍

---

### Scenario 4: Primary Serviceman Cancels

**Situation:** Primary serviceman has an emergency and cannot complete job.

**Flow:**
1. Primary serviceman notifies admin
2. Admin reassigns the backup serviceman as new primary
3. Admin assigns new backup serviceman (optional)
4. All parties receive updated notifications
5. **Result:** Service delivery not interrupted ✅

---

## ✅ Best Practices

### For Clients:

1. **Research Before Selecting**
   - Check serviceman ratings and reviews
   - Look at total jobs completed
   - Consider availability status

2. **Preference ≠ Guarantee**
   - Understand that admin makes final decision
   - Your preference is a strong recommendation, not a requirement

3. **Skip If Uncertain**
   - It's perfectly fine to let admin choose
   - Admin will select the best available serviceman

---

### For Admins:

1. **Always Respect Client Preference When Possible**
   - If preferred serviceman is available and qualified, assign them
   - Only override if there's a good reason (unavailable, overbooked, etc.)

2. **Always Assign a Backup Serviceman**
   - Ensures service continuity
   - Shows professionalism
   - Reduces delays if primary cancels

3. **Consider These Factors:**
   - ⭐ Serviceman rating and reviews
   - 📊 Current workload and availability
   - 📍 Location/proximity to job site
   - 🎯 Skill match for the job
   - 💡 Client's preference (if provided)

4. **Add Notes When Overriding Preference**
   - Explain to serviceman why they were chosen
   - Example: "Client's preferred serviceman was unavailable. You were selected based on high rating and availability."

5. **Monitor Backup Assignments**
   - Track when backups need to step in
   - Identify servicemen who frequently need backup coverage

---

### For Developers:

1. **Validation:**
   - Always validate serviceman approval status
   - Prevent same person as primary and backup
   - Check serviceman exists and is SERVICEMAN type

2. **Notifications:**
   - Send different notification content to primary vs backup
   - Include client contact info for primary only
   - Log all notification deliveries

3. **UI/UX:**
   - Make preferred serviceman optional (don't force selection)
   - Show "Skip" button clearly
   - Display client preference prominently in admin dashboard
   - Use visual indicators (icons, colors) for assignment status

---

## 🔒 Security & Permissions

### Who Can See What?

| Information | Client | Serviceman | Admin |
|------------|--------|------------|-------|
| Available servicemen list | ✅ Yes | ✅ Yes | ✅ Yes |
| Client's preferred serviceman | ✅ Own only | ❌ No | ✅ Yes |
| Assigned primary serviceman | ✅ Yes | ✅ If it's them | ✅ Yes |
| Assigned backup serviceman | ❌ No | ✅ If it's them | ✅ Yes |
| Client contact information | ❌ No | ✅ Primary only | ✅ Yes |

### Permission Requirements:

- **Browse servicemen:** Any authenticated user
- **Set preferred serviceman:** CLIENT only
- **Assign servicemen:** ADMIN only
- **View assignments:** Request owner or assigned serviceman or ADMIN

---

## 📊 Database Schema

```python
class ServiceRequest(models.Model):
    # Client info
    client = ForeignKey(User, related_name='client_requests')
    
    # Serviceman assignments (the three types)
    preferred_serviceman = ForeignKey(User, null=True, blank=True, 
                                     related_name='preferred_requests',
                                     help_text="Client's preference")
    serviceman = ForeignKey(User, null=True, blank=True, 
                           related_name='serviceman_requests',
                           help_text="Admin-assigned primary")
    backup_serviceman = ForeignKey(User, null=True, blank=True, 
                                  related_name='backup_requests',
                                  help_text="Admin-assigned backup")
    
    # ... other fields
```

---

## 🎯 Summary

**Three-Tier System:**
1. 💡 **Preferred** - Client's wish
2. ✅ **Primary** - Admin's assignment (the worker)
3. 🔄 **Backup** - Admin's safety net (the fallback)

**Key Benefits:**
- ✅ Gives clients control and choice
- ✅ Maintains admin oversight and quality
- ✅ Ensures service continuity with backup
- ✅ Increases customer satisfaction
- ✅ Reduces service delivery failures

**Remember:**
- Preferred serviceman is **optional**
- Primary serviceman is **required**
- Backup serviceman is **highly recommended**
- Only primary and backup receive notifications
- Admin has final say on assignments

---

**Questions? Issues? Check the full API documentation or contact the development team.**

**Last Updated:** November 5, 2025


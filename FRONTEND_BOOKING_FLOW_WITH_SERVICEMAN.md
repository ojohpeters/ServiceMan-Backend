# 🎯 Frontend: Booking Flow with Serviceman Selection

**CRITICAL:** How to send the serviceman the client clicked "Book Now" on

---

## 📋 The Complete Flow

```
1. Client browses servicemen
   ↓
2. Client clicks "Book Now" on a specific serviceman's card
   ↓
3. Frontend captures that serviceman's ID
   ↓
4. Client fills booking form (date, address, description)
   ↓
5. Client pays booking fee (Paystack)
   ↓
6. Frontend creates service request WITH preferred_serviceman_id
   ↓
7. Backend saves request with preferred_serviceman
   ↓
8. Admin sees client's preferred serviceman
```

---

## 🚨 CRITICAL: What Frontend Must Send

When creating a service request, **you MUST include `preferred_serviceman_id`** in the request body:

```javascript
POST /api/services/service-requests/

{
  "payment_reference": "PAY_xyz123",        // Required
  "category_id": 1,                         // Required
  "booking_date": "2025-11-15",             // Required
  "client_address": "123 Main St",          // Required
  "service_description": "Fix leaking pipe", // Required
  "is_emergency": false,                    // Optional
  "preferred_serviceman_id": 42             // ✨ THIS IS THE KEY!
}
```

**If you don't send `preferred_serviceman_id`, it will be `null`!**

---

## 💻 Frontend Implementation

### Method 1: Serviceman Profile Page (Recommended)

**URL Structure:** `/servicemen/:servicemanId/book`

```jsx
// ServicemanProfilePage.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';

function ServicemanProfilePage() {
  const { servicemanId } = useParams();  // ✅ Get from URL
  const navigate = useNavigate();
  const [serviceman, setServiceman] = useState(null);

  // When user clicks "Book Now" button
  const handleBookNow = () => {
    // ✅ Navigate to booking form with serviceman ID
    navigate('/book-service', {
      state: {
        preferredServicemanId: parseInt(servicemanId),
        servicemanName: serviceman?.user?.full_name,
        category: serviceman?.category
      }
    });
  };

  return (
    <div className="serviceman-profile">
      <h1>{serviceman?.user?.full_name}</h1>
      <p>⭐ {serviceman?.rating} rating</p>
      <p>📊 {serviceman?.total_jobs_completed} jobs completed</p>
      
      {/* Book Now Button */}
      <button 
        onClick={handleBookNow}
        className="btn-book-now"
      >
        📅 Book This Serviceman
      </button>
    </div>
  );
}
```

---

### Method 2: Serviceman Listing Page

**URL Structure:** `/servicemen?category=1`

```jsx
// ServicemenListPage.jsx
import { useNavigate } from 'react-router-dom';

function ServicemenListPage() {
  const navigate = useNavigate();
  const [servicemen, setServicemen] = useState([]);

  const handleBookServiceman = (serviceman) => {
    // ✅ Pass serviceman data to booking form
    navigate('/book-service', {
      state: {
        preferredServicemanId: serviceman.user.id,
        servicemanName: serviceman.user.full_name,
        category: serviceman.category
      }
    });
  };

  return (
    <div className="servicemen-grid">
      {servicemen.map(serviceman => (
        <div key={serviceman.id} className="serviceman-card">
          <h3>{serviceman.user.full_name}</h3>
          <p>⭐ {serviceman.rating}</p>
          <p>📊 {serviceman.total_jobs_completed} jobs</p>
          
          {/* Book Now Button */}
          <button onClick={() => handleBookServiceman(serviceman)}>
            Book Now
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

### Method 3: Booking Form Page

**URL Structure:** `/book-service` (receives serviceman data)

```jsx
// BookServicePage.jsx
import { useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

function BookServicePage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // ✅ Get preferred serviceman from navigation state
  const { 
    preferredServicemanId, 
    servicemanName, 
    category 
  } = location.state || {};

  const [bookingData, setBookingData] = useState({
    categoryId: category?.id || null,
    bookingDate: '',
    address: '',
    description: '',
    isEmergency: false
  });

  const [paymentReference, setPaymentReference] = useState(null);

  // Step 1: Initialize Payment
  const handlePayment = async () => {
    const amount = bookingData.isEmergency ? 5000 : 2000;
    
    const response = await fetch('/api/payments/initialize-booking-fee/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: amount,
        is_emergency: bookingData.isEmergency,
        callback_url: `${window.location.origin}/verify-payment`
      })
    });

    const data = await response.json();
    
    // Store booking data and preferred serviceman in localStorage
    localStorage.setItem('pendingBooking', JSON.stringify({
      ...bookingData,
      preferredServicemanId: preferredServicemanId,  // ✅ IMPORTANT!
      servicemanName: servicemanName
    }));
    
    // Redirect to Paystack
    window.location.href = data.authorization_url;
  };

  // Step 2: After Payment - Create Service Request
  const createServiceRequest = async (paymentRef) => {
    // Retrieve pending booking data
    const pendingBooking = JSON.parse(localStorage.getItem('pendingBooking') || '{}');
    
    const response = await fetch('/api/services/service-requests/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_reference: paymentRef,
        category_id: pendingBooking.categoryId,
        booking_date: pendingBooking.bookingDate,
        client_address: pendingBooking.address,
        service_description: pendingBooking.description,
        is_emergency: pendingBooking.isEmergency,
        preferred_serviceman_id: pendingBooking.preferredServicemanId  // ✅ SEND THIS!
      })
    });

    if (response.ok) {
      const serviceRequest = await response.json();
      
      // Clear localStorage
      localStorage.removeItem('pendingBooking');
      
      // Show success message
      if (serviceRequest.preferred_serviceman) {
        alert(`✅ Service request created!\n\nYour preferred serviceman: ${pendingBooking.servicemanName}\n\nAn admin will review and assign servicemen shortly.`);
      } else {
        alert('✅ Service request created! An admin will assign a serviceman shortly.');
      }
      
      // Redirect to requests page
      navigate('/my-requests');
    }
  };

  return (
    <div className="booking-form">
      <h2>Book Service</h2>

      {/* Show selected serviceman */}
      {preferredServicemanId && servicemanName && (
        <div className="preferred-serviceman-info">
          <h3>✓ You selected: {servicemanName}</h3>
          <p>This serviceman will be recommended to the admin for assignment.</p>
        </div>
      )}

      {/* Booking Form */}
      <form onSubmit={handlePayment}>
        <div className="form-group">
          <label>Category</label>
          <select 
            value={bookingData.categoryId || ''}
            onChange={(e) => setBookingData({...bookingData, categoryId: e.target.value})}
            required
          >
            <option value="">Select Category</option>
            <option value="1">Plumbing</option>
            <option value="2">Electrical</option>
            {/* ... more categories */}
          </select>
        </div>

        <div className="form-group">
          <label>Booking Date</label>
          <input 
            type="date"
            value={bookingData.bookingDate}
            onChange={(e) => setBookingData({...bookingData, bookingDate: e.target.value})}
            required
          />
        </div>

        <div className="form-group">
          <label>Service Address</label>
          <textarea
            value={bookingData.address}
            onChange={(e) => setBookingData({...bookingData, address: e.target.value})}
            required
            placeholder="Enter the full address where service is needed"
          />
        </div>

        <div className="form-group">
          <label>Service Description</label>
          <textarea
            value={bookingData.description}
            onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
            required
            placeholder="Describe the service you need in detail"
          />
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={bookingData.isEmergency}
              onChange={(e) => setBookingData({...bookingData, isEmergency: e.target.checked})}
            />
            Emergency Service (₦5,000 booking fee instead of ₦2,000)
          </label>
        </div>

        <div className="booking-summary">
          <p><strong>Booking Fee:</strong> ₦{bookingData.isEmergency ? '5,000' : '2,000'}</p>
          {preferredServicemanId && (
            <p><strong>Preferred Serviceman:</strong> {servicemanName}</p>
          )}
        </div>

        <button type="submit" className="btn-pay">
          Pay ₦{bookingData.isEmergency ? '5,000' : '2,000'} & Book Service
        </button>
      </form>
    </div>
  );
}
```

---

### Method 4: Payment Verification Page

**URL Structure:** `/verify-payment?reference=PAY_xyz123`

```jsx
// PaymentVerificationPage.jsx
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

function PaymentVerificationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const reference = searchParams.get('reference');

  useEffect(() => {
    if (reference) {
      verifyAndCreateRequest(reference);
    }
  }, [reference]);

  const verifyAndCreateRequest = async (paymentRef) => {
    try {
      // Step 1: Verify payment
      const verifyResponse = await fetch(
        `/api/payments/verify/?reference=${paymentRef}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      const verifyData = await verifyResponse.json();

      if (verifyData.status === 'success') {
        // Step 2: Get pending booking data
        const pendingBooking = JSON.parse(
          localStorage.getItem('pendingBooking') || '{}'
        );

        // Step 3: Create service request
        const requestResponse = await fetch('/api/services/service-requests/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            payment_reference: paymentRef,
            category_id: pendingBooking.categoryId,
            booking_date: pendingBooking.bookingDate,
            client_address: pendingBooking.address,
            service_description: pendingBooking.description,
            is_emergency: pendingBooking.isEmergency,
            preferred_serviceman_id: pendingBooking.preferredServicemanId  // ✅ CRITICAL!
          })
        });

        if (requestResponse.ok) {
          const serviceRequest = await requestResponse.json();
          
          // Clear localStorage
          localStorage.removeItem('pendingBooking');
          
          console.log('✅ Service Request Created:', serviceRequest);
          console.log('✅ Preferred Serviceman:', serviceRequest.preferred_serviceman);
          
          // Show success and redirect
          navigate('/booking-success', {
            state: { serviceRequest }
          });
        }
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return <div>Verifying payment and creating service request...</div>;
}
```

---

## 🔍 How to Debug

### Check if Frontend is Sending the Data

**In Browser Console:**
```javascript
// Before creating service request
const requestBody = {
  payment_reference: "PAY_xyz123",
  category_id: 1,
  booking_date: "2025-11-15",
  client_address: "123 Main St",
  service_description: "Fix leak",
  is_emergency: false,
  preferred_serviceman_id: 42  // ✅ Check this exists!
};

console.log('Request Body:', requestBody);
console.log('Has preferred_serviceman_id:', !!requestBody.preferred_serviceman_id);
console.log('Value:', requestBody.preferred_serviceman_id);
```

### Check Backend Response

**Expected Response (SUCCESS):**
```json
{
  "id": 789,
  "client": {...},
  "preferred_serviceman": {
    "id": 42,
    "user": {
      "full_name": "John Plumber"
    },
    "rating": "4.70"
  },
  "serviceman": null,
  "backup_serviceman": null,
  "status": "PENDING_ADMIN_ASSIGNMENT"
}
```

**Current Response (PROBLEM):**
```json
{
  "id": 789,
  "client": {...},
  "preferred_serviceman": null,  // ❌ This means frontend didn't send preferred_serviceman_id
  "serviceman": null,
  "backup_serviceman": null
}
```

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: CLIENT BROWSES SERVICEMEN                              │
│  GET /api/users/servicemen/?category=1                          │
│                                                                  │
│  Response:                                                       │
│  [                                                               │
│    {                                                             │
│      "id": 42,                                                   │
│      "user": { "id": 42, "full_name": "John Plumber" },         │
│      "rating": "4.70",                                           │
│      ...                                                         │
│    }                                                             │
│  ]                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: CLIENT CLICKS "BOOK NOW" ON SERVICEMAN #42             │
│                                                                  │
│  Frontend captures:                                              │
│  - servicemanId = 42                                             │
│  - servicemanName = "John Plumber"                               │
│  - category = { id: 1, name: "Plumbing" }                       │
│                                                                  │
│  Navigate to: /book-service                                      │
│  Pass via: location.state or localStorage                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: CLIENT FILLS BOOKING FORM                              │
│                                                                  │
│  - Category: Plumbing (from selected serviceman)                │
│  - Date: 2025-11-15                                             │
│  - Address: 123 Main St                                         │
│  - Description: Fix leaking pipe                                │
│  - Emergency: No                                                │
│                                                                  │
│  ✅ preferredServicemanId: 42 (stored)                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: PAYMENT INITIALIZATION                                 │
│  POST /api/payments/initialize-booking-fee/                     │
│                                                                  │
│  Request:                                                        │
│  {                                                               │
│    "amount": 2000,                                              │
│    "is_emergency": false,                                       │
│    "callback_url": "http://localhost:3000/verify-payment"      │
│  }                                                               │
│                                                                  │
│  Before redirect:                                                │
│  ✅ localStorage.setItem('pendingBooking', {                     │
│       preferredServicemanId: 42,  // SAVE THIS!                 │
│       categoryId: 1,                                             │
│       ...other booking data                                      │
│     })                                                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: PAYSTACK PAYMENT                                       │
│  User pays on Paystack → Redirected back to app                │
│  URL: /verify-payment?reference=PAY_xyz123                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: CREATE SERVICE REQUEST                                 │
│  POST /api/services/service-requests/                           │
│                                                                  │
│  Request Body:                                                   │
│  {                                                               │
│    "payment_reference": "PAY_xyz123",                           │
│    "category_id": 1,                                            │
│    "booking_date": "2025-11-15",                                │
│    "client_address": "123 Main St",                             │
│    "service_description": "Fix leaking pipe",                   │
│    "is_emergency": false,                                       │
│    "preferred_serviceman_id": 42  ← ✅ MUST INCLUDE THIS!       │
│  }                                                               │
│                                                                  │
│  Response:                                                       │
│  {                                                               │
│    "id": 789,                                                   │
│    "preferred_serviceman": {                                     │
│      "id": 42,                                                  │
│      "user": { "full_name": "John Plumber" }                    │
│    },                                                            │
│    ...                                                           │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist for Frontend

- [ ] When user clicks "Book Now" on a serviceman, capture `serviceman.user.id`
- [ ] Store `preferredServicemanId` in component state or localStorage
- [ ] Pass `preferredServicemanId` through navigation or localStorage
- [ ] Before payment redirect, save `preferredServicemanId` in localStorage
- [ ] After payment, retrieve `preferredServicemanId` from localStorage
- [ ] Include `preferred_serviceman_id` in service request creation body
- [ ] Verify response has `preferred_serviceman` object (not null)
- [ ] Clear localStorage after successful creation
- [ ] Show success message with serviceman name

---

## 🚨 Common Mistakes to Avoid

### ❌ WRONG: Not sending preferred_serviceman_id
```javascript
const response = await fetch('/api/services/service-requests/', {
  method: 'POST',
  body: JSON.stringify({
    payment_reference: "PAY_xyz123",
    category_id: 1,
    // ❌ Missing preferred_serviceman_id!
  })
});
// Result: preferred_serviceman will be null
```

### ✅ CORRECT: Including preferred_serviceman_id
```javascript
const response = await fetch('/api/services/service-requests/', {
  method: 'POST',
  body: JSON.stringify({
    payment_reference: "PAY_xyz123",
    category_id: 1,
    preferred_serviceman_id: 42  // ✅ Include this!
  })
});
// Result: preferred_serviceman will be the full serviceman object
```

---

## 🎯 Summary

**Backend is ready and working!** ✅

**Frontend needs to:**
1. Capture serviceman ID when user clicks "Book Now"
2. Store it through the booking flow
3. Send it as `preferred_serviceman_id` when creating service request

**The field is optional** - if frontend doesn't send it, `preferred_serviceman` will be `null` (which is fine, admin can assign anyone).

**But to honor client's choice**, frontend MUST send `preferred_serviceman_id`!

---

**Last Updated:** November 5, 2025  
**Status:** Backend Ready ✅ | Frontend Implementation Needed 🔄

